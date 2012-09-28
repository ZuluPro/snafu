from django.conf import settings

from sendim.models import *
from sendim.connection import *
from referentiel.models import *
from referentiel.defs import getReference


def createTicket(eventPk) :
    loginInfo = doLogin()
    if 'error' in loginInfo : return None

    E = Event.objects.get(pk=eventPk)
    R = E.getReference()

    # Creation du 1er contenu du ticket
    content = "Descriptif : "+ E.message +"\nImpact :\nDate et heure : " +str(E.date)+ u"\nV\xe9rification : "

    ticket= {
    	'session':loginInfo['session'],
    	'type':1,
    	'category': R.glpi_category.glpi_id,
    	'title': E.element.host+' '+E.message,
    	'content':content,
    	'recipient': R.glpi_dst_group.glpi_id,
    	'group':9,
    	'source': 'Supervision',
    	'itemtype' : E.element.host_type,
    	'item' : E.element.glpi_id,
    	'urgency': R.glpi_urgency.glpi_id,
    	'impact': R.glpi_impact.glpi_id
    }
    ticketInfo = glpiServer.glpi.createTicket(ticket)
    logprint( "Ticket #"+str(ticketInfo['id'])+" created", 'green' )

    # Sauvegarde dans BDD
    E.glpi = ticketInfo['id']
    E.save()
    logprint( "Ticket #"+str(ticketInfo['id'])+" associate to Event #"+str(E.pk), 'green')

    doLogout()
    return ticketInfo['id']

def addFollowUp(ticketId,content) :
    loginInfo = doLogin()
    E = Event.objects.get(pk=eventPk)
    contentToAdd = { 'session':idSessionGlpi, 'ticket':ticketId, 'content':content }
    glpiServer.glpi.addTicketFollowup(contentToAdd)
    doLogout()

def addMail(ticketId, msg) :
	content = """from: """ +settings.SNAFU['smtp-from']+ """
to: """+msg['To']+"""
cc: """+msg['Cc']+"""
subject: """+msg['Subject']+"""
"""+msg['body']
	
	addFollowUp(ticketId,content)

def getTicket(ticketId) :
    return glpiServer.glpi.getTicket({'session':idSession, 'ticket':ticketId})
