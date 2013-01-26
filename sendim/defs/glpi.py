"""
Function related to GLPI webservice.
"""

from django.conf import settings

from sendim.connection import doLogin, doLogout, glpiServer
from sendim.exceptions import UnableToConnectGLPI

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

def list_from_glpi(itemtype) :
    loginInfo = doLogin()

    if 'error' in loginInfo :
        raise UnableToConnectGLPI(loginInfo['error'])

    elif itemtype == 'host' :
        result = list()
        for itemtype in ('computer','networkequipment') :
            result += glpiServer.glpi.listObjects({'session':loginInfo['session'], 'itemtype':itemtype})

    else :
        data = {'session':loginInfo['session'], 'itemtype':itemtype} 
        result = glpiServer.glpi.listObjects(data)

    doLogout()
    return result

def get_from_glpi(itemtype, glpi_id) :
    loginInfo = doLogin()
    if 'error' in loginInfo :
        raise UnableToConnectGLPI(loginInfo['error'])

    elif itemtype == 'host' :
        result = list()
        for itemtype in ('computer','networkequipment') :
            result += glpiServer.glpi.listObjects({'session':loginInfo['session'], 'itemtype':itemtype})

    else :
        data = {'session':loginInfo['session'], 'itemtype':itemtype, 'id':glpi_id} 
        result = glpiServer.glpi.getObject(data)

    doLogout()
    return result
