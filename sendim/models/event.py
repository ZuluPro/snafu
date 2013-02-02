from django.db.models import Q
from django.db import models
from django.conf import settings

from referentiel.models import Host, Status
from sendim.models import MailTemplate
from sendim.exceptions import UnableToConnectGLPI
from sendim.defs import addMail, opengraph

from smtplib import SMTP
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Event(models.Model) :
    element = models.ForeignKey(Host)
    date = models.DateTimeField()
    criticity = models.CharField(max_length=30)
    message = models.CharField(max_length=300)
    glpi = models.IntegerField(blank=True, null=True)
    mail = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)

    class Meta:
        app_label = 'sendim'

    def __unicode__(self) :
        return str(self.pk)+':'+self.element.name+' - '+self.message

    def get_alerts(self, isUp=True, withoutRef=False):
        from sendim.models import Alert
        """
        Return a QuerySet of event's alerts.
        It is possible to filter with 2 arguments :
         - isUp : If False excludes UP/OK alerts.
         - withoutRef = If True excludes alerts without reference.
        """
        As = Alert.objects.filter(event=self).order_by('-date')
	if not isUp : As = As.exclude( Q(status__name__exact='OK') | Q(status__name__exact='UP') )
	if withoutRef : As = As.filter(reference=None)
        return As

    def get_last_alert(self, isUp=False):
        from sendim.models import Alert
        As = Alert.objects.filter(event=self).order_by('-date')
	if not isUp : As = As.exclude( Q(status__name__exact='OK') | Q(status__name__exact='UP') )
        return As[0]

    def get_primary_alert(self):
        """
        Return primary alert of event.
        if there's no primary alert, set the first as primary.
        """
        from sendim.models import Alert
        try : return Alert.objects.filter(event=self).get(isPrimary=True)
        except Alert.DoesNotExist :
            if self.get_alerts() :
                A = self.get_alerts()[0]
                #logprint("Event #"+str(self.pk)+" had no primary alert, set to the first Alert #"+str(A.pk), 'red')
                A.set_primary()
                return A
            else :
                try : self.delete()
                except AssertionError : pass
                return None
                #logprint("Event #"+str(self.pk)+" had no alert, it has been deleted", 'red')
        except Alert.MultipleObjectsReturned :
            A = self.get_alerts().filter(isPrimary=True)[0]
            A.set_primary()
            return A
            
    def create_ticket(self):
         """
         Create a GLPI ticket and add ticket number to self.glpi.
         """
         from sendim.connection import doLogin, doLogout, glpiServer

         loginInfo = doLogin()
         if 'error' in loginInfo :
             raise UnableToConnectGLPI
     
         R = self.get_reference()
     
         # Creation du 1er contenu du ticket
         content = "Descriptif : "+ self.message +"\nImpact :\nDate et heure : " +str(self.date)+ u"\nV\xe9rification : "
     
         item = self.element.glpi_id
         if item is None : item = 0

         if not R :
             category = 1
             recipient = source = 0
             urgency = impact = 3
         else :
             category = R.glpi_category.glpi_id
             recipient = R.glpi_dst_group.glpi_id
             source = R.glpi_source
             urgency = R.glpi_urgency.glpi_id
             impact = R.glpi_impact.glpi_id

         ticket= {
             'session':loginInfo['session'],
             'type':1,
             'category': category,
             'title': self.element.name+' '+self.message,
             'content':content,
             'recipient': recipient,
             'group':9,
             'source': source,
             #'itemtype' : self.element.host_type,
             #'item' : item,
             'urgency':urgency,
             'impact':impact,
         }
         ticketInfo = glpiServer.glpi.createTicket(ticket)
         #logprint( "Ticket #"+str(ticketInfo['id'])+" created", 'green' )
     
         # Sauvegarde dans BDD
         self.glpi = ticketInfo['id']
         self.save()
         #logprint( "Ticket #"+str(ticketInfo['id'])+" associate to Event #"+str(self.pk), 'green')
     
         doLogout()
         return ticketInfo['id']

    def get_reference(self):
        """Return reference of primary alert."""
    	return self.get_primary_alert().reference

    def close(self, force=False):
        """
        Calculate if the event may be closed.
        If yes :  Close event
        If no : Do nothing, or close if force=True in arguments.
        """
        
        if self.closed : return False
        else :
            hosts = {}
            for A in self.get_alerts() :
                if not A.host.name in hosts : hosts[A.host.name] = []
                if not A.service.name in hosts[A.host.name] : hosts[A.host.name].append(A.service.name)
            ### Calcul de tout les service
            notOK = list()
            for host in hosts.keys() : 
                for service in hosts[host] :
                    if service == 'Host status' :
                        if not self.get_alerts().filter(host__name=host,service__name=service,status=Status.objects.get(name='UP') ) :
                            notOK.append( (host,service) )
                    else :
                        if not self.get_alerts().filter(host__name=host,service__name=service,status=Status.objects.get(name='OK') ) :
                            notOK.append( (host,service) )
            if not notOK :
                self.closed = True
                self.save()
        return self.closed 

    def make_mail(self):
        """
        Using Event and the chosen MailTemplate for create
        a dictionnary which contains all mail attributes.
        """
        R = self.get_primary_alert().reference
        if MailTemplate.objects.filter(chosen=True).exists() :
            MT = MailTemplate.objects.get(chosen=True)
        else :
            MT = MailTemplate.objects.get(pk=1)
    
        msg = {}
        msg['from'] = settings.SNAFU['smtp-from']
        msg['to'] = R.mail_group.to
        if self.criticity == 'Majeur' : msg['to'] += ', '+ R.mail_group.ccm
        msg['cc'] = ' ,'.join( [  settings.SNAFU['smtp-from'], R.mail_group.cc] )
        msg['subject'] = MT.subject
        msg['body'] = MT.body
    
        return msg

    def send_mail(self,POST):
        """
        Use request.POST from 'sendim/templates/event/preview-mail.html',
        for send an email.
        This function make all substitutions before processing.
        After send, add mail to GLPI ticket.
        """
        A = self.get_primary_alert()
        # Recherche du MailGroup correspondant
        R = A.reference
    
        msg = MIMEMultipart()
        msg['From'] = settings.SNAFU['smtp-from']
        msg['To'] = POST['to']
        if POST['ccm'] : msg['To'] += ', '+ R.mail_group.ccm
     
        mailSub = POST['subject']
        mailText = POST['body']
    
        # Make substitutions
        SUBS = (
            ("$HOST$", A.host.name),
            ("$MESSAGE$", self.message),
            ("$MAIL_TYPE$", R.mail_type.name),
            ("$CRITICITY$", self.criticity),
            ("$GLPI$" , str(self.glpi)),
            ("$GLPI-URL$", settings.SNAFU['glpi-url']+'front/ticket.form.php?id='),
            ("$TRANSLATION", self.message),
            ("$DATETIME$", self.date.strftime('%d/%m/%y - %H:%M:%S')),
            ("$DATE$", self.date.strftime('%d/%m/%y')),
            ("$TIME$", self.date.strftime('%H:%M:%S')),
            ("$LOG$" , '\n'.join( [ A.date.strftime('%d/%m/%y %H:%M:%S - ')+A.service.name+' en ' +A.status.name+' - '+A.info for A in self.get_alerts() ] ) )
        ) 
        for pattern,string in SUBS :
            mailText = mailText.replace(pattern, string)
            mailSub = mailSub.replace(pattern, string)
        msg['Subject'] = mailSub
        msg.attach( MIMEText( mailText.encode('utf8') , 'plain' ) )
        
        # Add graph to mail
        if 'graphList' in POST :
            graphList = POST.getlist('graphList')
            for i in range(len(graphList)) :
                pagehandle = opengraph(A, graphList[i])
                #pagehandle2 = opengraph(A, graphList[i][0])
                msg.attach( MIMEImage( pagehandle ) )
                #msg.attach( MIMEImage( pagehandle2 ) )
    
        # Send mail
        smtpObj = SMTP(settings.SNAFU['smtp-server'] , settings.SNAFU['smtp-port'] )
        if 'smtp-password' in settings.SNAFU.keys() :
            smtpObj.ehlo()
            smtpObj.starttls()
            smtpObj.ehlo()
            smtpObj.login(settings.SNAFU['smtp-from'], settings.SNAFU['smtp-password'])
        smtpObj.sendmail( msg['From'] , ( msg['To'], msg['Cc'] ), msg.as_string() )
    
        self.mail=True
        self.save()

        msg['body'] = mailText
        addMail(self.glpi, msg)
    
        return True
