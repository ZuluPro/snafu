from django.conf import settings

from sendim.models import *
from referentiel.models import *
from referentiel.defs import getReference

import xmlrpclib

serverUrl = settings.SNAFU['glpi-xmlrpc']
server = xmlrpclib.Server(serverUrl, verbose=False, allow_none=True)
loginData = { 'login_name':settings.SNAFU['glpi-login'], 'login_password':settings.SNAFU['glpi-password'] }

#try :
loginInfo = server.glpi.doLogin( loginData )
#except xmlrpclib.Fault as inst : print 123

idSession=loginInfo['session']

def createTicket(eventPk) :
	E = Event.objects.get(pk=eventPk)
	R = E.getReference()

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
	logprint( "Ticket #"+str(ticketInfo['id'])+" created", 'green' )

	# Sauvegarde dans BDD
	E.glpi = ticketInfo['id']
	E.save()
	logprint( "Ticket #"+str(ticketInfo['id'])+" associate to Event #"+str(E.pk), 'green')

        return ticketInfo['id']

def addFollowUp(ticketId,content) :
    contentToAdd = { 'session':idSession, 'ticket':ticketId, 'content':content }
    server.glpi.addTicketFollowup(contentToAdd)

def addMail(ticketId, msg) :
	content = """from: """ +settings.SNAFU['smtp-from']+ """
to: """+msg['To']+"""
cc: """+msg['Cc']+"""
subject: """+msg['Subject']+"""
"""+msg['body']
	
	addFollowUp(ticketId,content)

def getTicket(ticketId) :
    return server.glpi.getTicket({'session':idSession, 'ticket':ticketId})
