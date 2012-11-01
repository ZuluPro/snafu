"""
Function related to GLPI webservice.
"""

from django.conf import settings

from sendim.models import *
from sendim.connection import *
from sendim.exceptions import UnableToConnectGLPI
from referentiel.models import *
from referentiel.defs import getReference


def createTicket(E) :
    """
    Create a GLPI ticket for the given Event object.
    Add ticket number to Event.glpi.
    """
    loginInfo = doLogin()
    if 'error' in loginInfo :
        raise UnableToConnectGLPI

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
    	'source': R.glpi_source,
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
    """
    Add a content to the given ticket number.
    """
    loginInfo = doLogin()
    contentToAdd = { 'session':loginInfo['session'], 'ticket':ticketId, 'content':content }
    glpiServer.glpi.addTicketFollowup(contentToAdd)
    doLogout()

def addMail(ticketId, msg) :
    """
    Use method addFollowUp() for add the given mail object to ticket.
    """
    content = "from: " +settings.SNAFU['smtp-from']+ "\nto: " +msg['To']#+ "cc: " +msg['Cc'] +"subject: " +msg['Subject']+ "\n" +msg['body']
    addFollowUp(ticketId,content)

def getTicket(ticketId) :
    """
    Return a dictionnary with ticket's attributes.

    Below, a short list of them :
    - General :
     - name
     - content
     - solution 
     - status

    - related to date :
     - date
     - date_mod

    - Users and Groups:
     - users_id_lastupdater
     - users_name_lastupdater
     - users_name_recipient
     - users_id_recipient
     - users :
      - requester
      - assign
     - groups :
      - requester
      - assign

    - Items :
     - itemtype
     - items_id
     - items_name
     - itemtype_name

    - Category :
     - type
     - type_name
     - ticketcategories_id
     - ticketcategories_name
    """
    return glpiServer.glpi.getTicket({'session':idSession, 'ticket':ticketId})

def get_hosts_from_glpi() :
    loginInfo = doLogin()
    if 'error' in loginInfo :
        raise UnableToConnectGLPI(loginInfo['error'])
    hosts = list()
    for itemtype in ('computer','networkequipment') :
        data = {
          'session':loginInfo['session'],
          'itemtype': 'computer',
          'limit':2000
        }
        for host in glpiServer.glpi.listObjects(data) :
            if not host in hosts :
                hosts.append(host)

    doLogout()
    return hosts

#def get_categories_from_glpi() :
#    loginInfo = doLogin()
#    cats = list()
#    for itemtype in ('computer','networkequipment') :
#        data = {
#          'session':loginInfo['session'],
#          'itemtype': 'computer',
#          'limit':2000
#        }
#        for host in glpiServer.glpi.listObjects(data) :
#            if not host in hosts :
#                hosts.append(host)
#
#    doLogout()
#    return hosts
