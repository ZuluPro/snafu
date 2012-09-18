from django.db.models import Q
from django.conf import settings
from sendim.models import *
from referentiel.models import *

import exceptions
import codecs,locale
import sys, os , datetime, time, re
from glpidict import *
import smtplib
from time import strftime
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import urllib2, HTMLParser
import xmlrpclib

#import djcelery
#from sendim.celery import celery 

# Connexion a glpi
serverUrl = settings.SENDIM['glpi-url']
server = xmlrpclib.Server(serverUrl, verbose=False, allow_none=True)
loginData = { 'login_name':settings.SENDIM['glpi-login'], 'login_password':settings.SENDIM['glpi-password'] }
loginInfo = server.glpi.doLogin( loginData )
idSession=loginInfo['session']

# Connexion a Nagios
www = settings.SENDIM['nagios-url']
username = settings.SENDIM['nagios-login']
password = settings.SENDIM['nagios-password']
htmlparser = HTMLParser.HTMLParser()

passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
passman.add_password(None, www, username, password)
authhandler = urllib2.HTTPBasicAuthHandler(passman)
opener = urllib2.build_opener(authhandler)
urllib2.install_opener (opener)

#@celery.task()
def readNagios() :# Retourne une liste de liste : host,service,status,info,date
        pagehandle = opener.open(www+'nagios/cgi-bin/history.cgi?host=all&archive=0&statetype=2&type=0&noflapping=on')
	problemlist = []
	for line in pagehandle.readlines()[::-1] :
		if re.search( r"<img align='left'" , line ) :
			line = htmlparser.unescape( line[:-1] )

			if re.search( 'SERVICE ALERT' , line ) :
				problemlist.append( [ re.sub( r"^.*ALERT: ([^;]*);.*" , r"\1" , line ),
						re.sub( r".*ALERT: [^;]*;([^;]*);.*$" , r"\1" , line ),
						re.sub( r".*ALERT: [^;]*;[^;]*;([^;]*);.*$" , r"\1" , line ),
						re.sub( r".*ALERT: [^;]*;[^;]*;[^;]*;[^;]*;[^;]*;([^;]*)<br clear='all' />$" , r"\1" , line ),
						re.sub( r".*>\[([^\]]*)\].*" , r"\1" , line ) ] )

			elif re.search( 'HOST ALERT' , line ) :
				problemlist.append( [ re.sub( r"^.*ALERT: ([^;]*);.*" , r"\1" , line ),
						"Host status",
						re.sub( r".*ALERT: [^;]*;([^;]*);.*$" , r"\1" , line ),
						re.sub( r".*ALERT: [^;]*;[^;]*;[^;]*;[^;]*;([^;]*).*<br clear='all' />$" , r"\1" , line ),
						re.sub( r".*>\[([^\]]*)\].*" , r"\1" , line ) ] )
	return problemlist

def readGraphs(host,service=None):
    try :
        if service != None : pagehandle = opener.open(www+'pnp4nagios/graph?host='+host+'&srv='+service.replace(' ' , '+')+'&view=0' )
        else : pagehandle = opener.open(www+'pnp4nagios/graph?host='+host)
    except : pass
    else:
        graphList = list()
        count = 0
        for line in pagehandle.readlines() :
            if re.match(r'<td.*Datasource:[^\<]*' , line ) :
                graphList.append( ( count, re.sub( r".*Datasource: ([^\<]*).*" , r"\1" , line ) ) )
                count+=1
        return graphList

#@celery.task()
def reloadAlert(contentMsg='') :
        print 'Insertion des alerts'
	for host,service,status,info,date in readNagios() :
		# Conversion de la date nagios en object datetime
                try : date = datetime.datetime.fromtimestamp( time.mktime( time.strptime(date, "%Y-%m-%d %H:%M:%S")) )
                except : print u"Date invalide: "+date; date = time.strftime("%Y-%m-%d %H:%M:%S")
		# Compare la liste a la BDD, si ya pas une ligne avec le meme host,service,date
		# Cause une erreur si non trouve

		# Recherche de l'hote dans BDD
		try : Host.objects.get(host=host)
		except : Host(host=host).save() ; print "Ajout de l'Host "+host

		# Recherche du service dans BDD
		try : Service.objects.get(service=service)
		except : Service(service=service).save() ; print "Ajout du service "+service

		# Recherche si l'alerte existe deja
		try : Alert.objects.get(host__host__exact=host, service__service__exact=service, date=date )
		except :
			alert = Alert(
				host = Host.objects.get(host=host),
				service = Service.objects.get(service=service),
				status = Status.objects.get(status=status),
				info=info,
				date=date
			)
			alert.save() ; print "Creation de l'Alert #"+str(alert.pk)
                        contentMsg += u"Cr\xe9ation de l'Alert #"+str(alert.pk)+" : " +alert.service.service+ " sur " +alert.host.host+ '<br>'
        return contentMsg

def sendMail( POST) :
	E = Event.objects.get(pk=POST['eventPk'])
	A = Alert.objects.get(pk=POST['alertPk'])
	# Recherche du MailGroup correspondant
	R = Reference.objects.filter(host__host__exact=A.host.host, service__service__exact=A.service.service, status__status__exact=A.status.status )[0]

	msg = MIMEMultipart()
	msg['From'] = settings.SENDIM['smtp-from']
        msg['To'] = POST['to']
	if POST['ccm'] : msg['To'] += ', '+ R.mail_group.ccm
	msg['Cc'] = POST['cc']
	msg['Subject'] = POST['subject']

	mailText = POST['body']
	mailText = re.sub( r"\$HOST\$" , A.host.host, mailText )
	mailText = re.sub( r"\$GLPI\$" , str(E.glpi) , mailText )
	mailText = re.sub( r"\$TRADUCTION\$" , E.message , mailText)
	mailText = re.sub( r"\$JOUR\$" , E.date.strftime('%d/%m/%y') , mailText)
	mailText = re.sub( r"\$HEURE\$" , E.date.strftime('%H:%M:%S') ,  mailText)
	mailText = re.sub( r"\$LOG\$" , '\n'.join( [ alert.date.strftime('%d/%m/%y %H:%M:%S - ')+alert.service.service+' - '+alert.info for alert in Alert.objects.filter(event__pk=E.pk) ] ),  mailText)
	msg.attach( MIMEText( mailText.encode('utf8') , 'plain' ) )
	
	# Ajout des graphs slelectinnes
        print POST.getlist('graphList')
	if 'graphList' in POST :
                graphList = POST.getlist('graphList')
		for i in range(len(graphList)) :
                        print "Ajout d'un graph pour "+graphList[i]
			pagehandle = opener.open(www+'pnp4nagios/image?host='+A.host.host+'&srv='+A.service.service.replace(' ' , '+')+'&view=1&source='+str(int(graphList[i][0]) ) ).read()
			pagehandle2 = opener.open(www+'pnp4nagios/image?host='+A.host.host+'&srv='+A.service.service.replace(' ' , '+')+'&view=2&source='+str(int(graphList[i][0]) ) ).read()
			msg.attach( MIMEImage( pagehandle ) )
			msg.attach( MIMEImage( pagehandle2 ) )

	smtpObj = smtplib.SMTP(settings.SENDIM['smtp-server'] , settings.SENDIM['smtp-port'] )
	smtpObj.sendmail( msg['From'] , ( msg['To'], msg['Cc'] ), msg.as_string() )

	E.mail = True
	E.save()
	print "Mail envoye pour l'evenement #"+str(E.pk)
        msg['body'] = mailText
        addMail(E.glpi, msg)


def createTicket(eventPk, alertPk) :
	E = Event.objects.get(pk=eventPk)
	A = Alert.objects.get(pk=alertPk)
	# Recherche de la reference
	R = Reference.objects.filter(host__host__exact=A.host.host, service__service__exact=A.service.service, status__status__exact=A.status.status )[0]

	# Creation du 1er contenu du ticket
	content = "Descriptif : "+ E.message +"\nImpact :\nDate et heure : " +str(E.date)+ u"\nV\xe9rification : "

        ticket= {
		'session':idSession,
		'type':1,
		'category': R.glpi_category.glpi_id,
		'title': E.element.host+' '+E.message,
		'content':content,
		'recipient': R.glpi_dst_group.glpi_id,
		'group':9, # Autolib Exploitation
		'source': 'Supervision',
		'itemtype' : E.element.host_type,
		'item' : E.element.glpi_id,
		'urgency': R.glpi_urgency.glpi_id,
		'impact': R.glpi_impact.glpi_id
	}
        ticketInfo = server.glpi.createTicket(ticket)
	print "Ticket #"+str(ticketInfo['id'])+" cree"

	# Sauvegarde dans BDD
	E.glpi = ticketInfo['id']
	E.save()
	print "Ticket #"+str(ticketInfo['id'])+" associe a l'Event #"+str(E.pk)

        return ticketInfo['id']

def addMail(ticketId, msg) :
	content = """from: """ +settings.SENDIM['smtp-from']+ """
to: """+msg['To']+"""
cc: """+msg['Cc']+"""
subject: """+msg['Subject']+"""
"""+msg['body']
	
	contentToAdd = { 'session':idSession, 'ticket':ticketId, 'content':content }
	server.glpi.addTicketFollowup(contentToAdd)

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

def treatAlerts(contentMsg='') :
    contentMsg += reloadAlert() # reloadAlert retourne un message en HTML
    ## Recherche des alerts n'ayant pas d'Event
    for alert in Alert.objects.filter(event=None, date__gte=datetime.datetime(2012, 8, 24, 18, 19, 6, 957325)) :
        try : # Execept Si pas d'alerte trouve
          lastAlert = Alert.objects.filter( Q(host=alert.host) & Q(service=alert.service) & ~Q(date__gt=alert.date) & ~Q(event=None) ).order_by('-pk')[0]
          lastEvent = lastAlert.event
          if not re.search( r"(OK|UP)", lastAlert.status.status ):
              alert.event = lastEvent ; alert.save()
              print "Ajout automatique de l'alert #" +str(alert.pk)+ "a l'Event #" +str(lastEvent.pk)
          else : raise exceptions.StandardError
        except : 
            E = Event()
            try :
                Reference.objects.filter(host__host__exact=alert.host.host, service__service__exact=alert.service.service )[0]
                if re.search(r'(OK|UP)', alert.status.status) : tempStatus='WARNING'
                else : tempStatus = alert.status.status
                E.criticity= Reference.objects.filter(host__host__exact=alert.host.host, service__service__exact=alert.service.service, status__status__exact=tempStatus )[0].mail_criticity
            except : E.criticity = "?"

            try :
                Traduction.objects.filter( service__service__exact=alert.service.service )[0]
                E.message = Traduction.objects.filter(service__service__exact=alert.service)[0].traduction
            except : E.message = alert.info
            
            E.element=alert.host; E.date=alert.date
            E.save()
            print "Creation de l'Event "+str(E.pk)
            alert.event = E
            alert.save()
            # contentMsg += "Association de l'Alert #" +str(alert.pk)+ u" \xe0  l'Event #" +str(E.pk)+ "<br>"
            print "Modification de l'alert #"+str(alert.pk)+" : Associe a l'Event #"+str(E.pk)
    return contentMsg

def makeMail(R,E,A,ticketId):
    msg = {} 
    msg['from'] = settings.SENDIM['smtp-from']
    msg['to'] = R.mail_group.to
    if E.criticity == 'Majeur' : msg['to'] += ', '+ R.mail_group.ccm
    msg['cc'] = ' ,'.join( [  settings.SENDIM['smtp-from'], R.mail_group.cc] )
    msg['subject'] = '[Incident '+R.mail_type.mail_type+' Autolib\' - '+E.criticity+'] '+E.date.strftime('%d/%m/%y')+' - '+ E.message +' sur ' +E.element.host +' - GLPI '+str(ticketId)
    with open('./mailforhost.txt' , 'r') as mailFile : msg['body'] = mailFile.read()
    
    return msg

def agregate(eventsPk, choicedEvent, message, glpi=None, mail=False) :
    for eventPk in eventsPk :
        if Event.objects.get(pk=eventPk).glpi : glpi= Event.objects.get(pk=eventPk).glpi
        if Event.objects.get(pk=eventPk).mail : mail= True
        if eventPk == choicedEvent: continue
        for alert in Alert.objects.filter(event=eventPk) :
            alert.event = Event.objects.get(pk=choicedEvent)
            alert.save()
            print "Alert #" +str(alert.pk)+" associe a l'Event #" +str(choicedEvent)
        Event.objects.get(pk=eventPk).delete()
        print "Suppression de l'Event #" +eventPk

        E = Event.objects.get(pk=choicedEvent)
        E.message = message
        E.glpi = glpi
        E.mail = mail
        E.save()
