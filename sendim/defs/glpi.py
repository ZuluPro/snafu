from django.conf import settings

from sendim.models import *
from referentiel.models import *

import xmlrpclib

serverUrl = settings.SENDIM['glpi-xmlrpc']
server = xmlrpclib.Server(serverUrl, verbose=False, allow_none=True)
loginData = { 'login_name':settings.SENDIM['glpi-login'], 'login_password':settings.SENDIM['glpi-password'] }

#try :
loginInfo = server.glpi.doLogin( loginData )
#except xmlrpclib.Fault as inst : print 123

idSession=loginInfo['session']

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


