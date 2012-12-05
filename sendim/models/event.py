from django.db.models import Q
from django.db import models

from referentiel.models import Host, Status
from sendim.exceptions import UnableToConnectGLPI

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

    def getAlerts(self, isUp=True, withoutRef=False):
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

    def getPrimaryAlert(self):
        """
        Return primary alert of event.
        if there's no primary alert, set the first as primary.
        """
        from sendim.models import Alert
        try : return Alert.objects.filter(event=self).get(isPrimary=True)
        except Alert.DoesNotExist :
            if self.getAlerts() :
                A = self.getAlerts()[0]
                #logprint("Event #"+str(self.pk)+" had no primary alert, set to the first Alert #"+str(A.pk), 'red')
                A.setPrimary()
                return A
            else :
                try : self.delete()
                except AssertionError : pass
                return None
                #logprint("Event #"+str(self.pk)+" had no alert, it has been deleted", 'red')
        except Alert.MultipleObjectsReturned :
            A = self.getAlerts().filter(isPrimary=True)[0]
            A.setPrimary()
            return A
            

    def create_ticket(self) :
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
     
         ticket= {
             'session':loginInfo['session'],
             'type':1,
             'category': R.glpi_category.glpi_id,
             'title': self.element.name+' '+self.message,
             'content':content,
             'recipient': R.glpi_dst_group.glpi_id,
             'group':9,
             'source': R.glpi_source,
             'itemtype' : self.element.host_type,
             'item' : self.element.glpi_id,
             'urgency': R.glpi_urgency.glpi_id,
             'impact': R.glpi_impact.glpi_id
         }
         ticketInfo = glpiServer.glpi.createTicket(ticket)
         #logprint( "Ticket #"+str(ticketInfo['id'])+" created", 'green' )
     
         # Sauvegarde dans BDD
         self.glpi = ticketInfo['id']
         self.save()
         #logprint( "Ticket #"+str(ticketInfo['id'])+" associate to Event #"+str(self.pk), 'green')
     
         doLogout()
         return ticketInfo['id']

    def sendMail(self) :
    	pass

    def get_reference(self) :
        """Return reference of primary alert."""
    	return self.getPrimaryAlert().reference

    def close(self, force=False):
        """
        Calculate if the event may be closed.
        If yes :  Close event
        If no : Do nothing, or close if force=True in arguments.
        """
        
        if self.closed : return False
        else :
            hosts = {}
            for A in self.getAlerts() :
                if not A.host.name in hosts : hosts[A.host.name] = []
                if not A.service.name in hosts[A.host.name] : hosts[A.host.name].append(A.service.name)
            ### Calcul de tout les service
            notOK = list()
            for host in hosts.keys() : 
                for service in hosts[host] :
                    if not self.getAlerts().filter(host__name=host,service__name=service,status=Status.objects.get(name='OK') ) :
                        notOK.append( (host,service) )
            if not notOK :
                self.closed = True
                self.save()
        return self.closed 

