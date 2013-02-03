"""
Function related to GLPI webservice.
"""

from django.conf import settings

from sendim.connection import doLogin, doLogout, glpiServer
from sendim.exceptions import UnableToConnectGLPI

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
    session = doLogin()['session']
    return glpiServer.glpi.getTicket({'session':session, 'ticket':ticketId})

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
