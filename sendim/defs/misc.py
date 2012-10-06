from django.forms.formsets import formset_factory
from django.conf import settings

from referentiel.models import *
from referentiel.defs import getReference 
from sendim.forms import *
from sendim.models import *
from sendim.defs import addMail,opengraph

from common import logprint
import re
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def sendMail(POST) :
	E = Event.objects.get(pk=POST['eventPk'])
	A = E.getPrimaryAlert()
	# Recherche du MailGroup correspondant
	R = A.reference

	msg = MIMEMultipart()
	msg['From'] = settings.SNAFU['smtp-from']
        msg['To'] = POST['to']
	if POST['ccm'] : msg['To'] += ', '+ R.mail_group.ccm
	msg['Cc'] = POST['cc']
	msg['Subject'] = POST['subject']
	mailText = POST['body']

	for pattern,string in ( (r"\$HOST\$", A.host.host), (r"\$GLPI\$" , str(E.glpi)), (r"\$GLPI-URL\$", settings.SNAFU['glpi-url']+'front/ticket.form.php?id='), (r"\$TRADUCTION\$", E.message), (r"\$DATE\$", E.date.strftime('%d/%m/%y - %H:%M:%S')), (r"\$JOUR\$", E.date.strftime('%d/%m/%y')), (r"\$HEURE\$", E.date.strftime('%H:%M:%S')), (r"\$LOG\$" , '\n'.join( [ alert.date.strftime('%d/%m/%y %H:%M:%S - ')+alert.service.service+' en ' +alert.status.status+' - '+alert.info for alert in Alert.objects.filter(event__pk=E.pk) ] ) ) ) : 
		mailText = re.sub( pattern , string, mailText )
		msg['Subject'] = re.sub( pattern,string, msg['Subject'] )
	msg.attach( MIMEText( mailText.encode('utf8') , 'plain' ) )
	
	# Ajout des graphs slelectinnes
	if 'graphList' in POST :
                graphList = POST.getlist('graphList')
		for i in range(len(graphList)) :
			pagehandle = opengraph(A, graphList[i][0])
			pagehandle2 = opengraph(A, graphList[i][0])
			msg.attach( MIMEImage( pagehandle ) )
			msg.attach( MIMEImage( pagehandle2 ) )
			logprint("Add " +graphList[i]+ "to mail" )

	smtpObj = smtplib.SMTP(settings.SNAFU['smtp-server'] , settings.SNAFU['smtp-port'] )
	if 'smtp-password' in settings.SNAFU.keys() :
		smtpObj.ehlo()
		smtpObj.starttls()
		smtpObj.ehlo()
		smtpObj.login(settings.SNAFU['smtp-from'], settings.SNAFU['smtp-password'])
	smtpObj.sendmail( msg['From'] , ( msg['To'], msg['Cc'] ), msg.as_string() )

	E.mail = True
	E.save()
        msg['body'] = mailText
        addMail(E.glpi, msg)



def addRef(POST):
    alert = Alert.objects.get( pk=POST['alertPk'] )
    R = Reference(
            host = Host.objects.get(pk=POST['host']),
            service = Service.objects.get(pk=POST['service']),
            status = Status.objects.get(pk=POST['status']),
            escalation_contact = POST['escalation_contact'],
            tendancy = POST['tendancy'],
            outage = POST['outage'],
            explanation = POST['explanation'],
            origin = POST['origin'],
            procedure = POST['procedure'],
            mail_type = MailType.objects.get(pk=POST['mail_type']),
            mail_group = MailGroup.objects.get(pk=POST['mail_group']),
            mail_criticity = MailCriticity.objects.get(pk=POST['mail_criticity']),
            glpi_urgency = GlpiUrgency.objects.get(pk=POST['glpi_urgency']),
            glpi_priority = GlpiPriority.objects.get(pk=POST['glpi_priority']),
            glpi_impact = GlpiImpact.objects.get(pk=POST['glpi_impact']),
            glpi_category = GlpiCategory.objects.get(pk=POST['glpi_category']),
            glpi_source = POST['glpi_source'],
            glpi_dst_group = GlpiGroup.objects.get(pk=POST['glpi_dst_group']),
            glpi_supplier = GlpiSupplier.objects.get(pk=POST['glpi_supplier'])
    )
    R.save()
    logprint('Reference #' +str(R.pk)+ ' saved', 'green')


def makeMail(E):
    R = E.getPrimaryAlert().reference
    MT = MailTemplate.objects.get(choosen=True)
    msg = {}
    msg['from'] = settings.SNAFU['smtp-from']
    msg['to'] = R.mail_group.to
    if E.criticity == 'Majeur' : msg['to'] += ', '+ R.mail_group.ccm
    msg['cc'] = ' ,'.join( [  settings.SNAFU['smtp-from'], R.mail_group.cc] )
    msg['subject'] = MT.subject 
    msg['body'] = MT.body
    
    return msg

def agregate(eventsPk, choicedEvent, message, glpi=None, mail=False, criticity='Mineur') :
    if len(eventsPk) < 2 : return None
    for eventPk in eventsPk :
        E = Event.objects.get(pk=eventPk)
        if E.glpi : glpi = E.glpi
        if E.mail : mail= True
        if E.criticity == 'Majeur' : criticity= 'Majeur'
        if eventPk == choicedEvent: continue
        for alert in E.getAlerts() :
            alert.isPrimary = False
            alert.event = Event.objects.get(pk=choicedEvent)
            alert.save()
            logprint("Add Alert #" +str(alert.pk)+ " to Event #" +str(choicedEvent) )
        E.delete()
        logprint("Delete Event #" +eventPk, 'pink')

        E = Event.objects.get(pk=choicedEvent)
        E.message = message
        E.glpi = glpi
        E.mail = mail
        E.criticity = criticity
        E.save()


def createServiceList(As, hosts={}):
    for A in As :
        if not A.host.host in hosts : hosts[A.host.host] = []
        if not A.service.service in hosts[A.host.host] : hosts[A.host.host].append(A.service.service)

    return hosts

def makeMultipleForm(hosts):
    ReferenceBigFormSet = formset_factory(ReferenceBigForm)
    data = {
       'form-TOTAL_FORMS' : sum( [ len(v) for v in hosts.values() ] ), 
       'form-INITIAL_FORMS': sum( [ len(v) for v in hosts.values() ] )
    }

    for count,(host,services) in enumerate(hosts.items()) :
        for service in services :
            data['form-'+str(count)+'-host'] = Host.objects.get(host=host)
            data['form-'+str(count)+'-service'] = Service.objects.get(service=service)
            data['form-'+str(count)+'-glpi_source'] = 'Supervision'
            for status in ('warning','critical','unknown') :
                data['form-'+str(count)+'-'+status+'_criticity'] = 1 
                data['form-'+str(count)+'-'+status+'_urgency'] = 3 
                data['form-'+str(count)+'-'+status+'_priority'] = 3 
                data['form-'+str(count)+'-'+status+'_impact'] = 4 
       
    return ReferenceBigFormSet(data)
