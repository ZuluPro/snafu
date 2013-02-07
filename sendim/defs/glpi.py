"""
Function related to GLPI webservice.
"""

from django.conf import settings

from sendim.connection import doLogin, doLogout, glpiServer
from sendim.exceptions import UnableToConnectGLPI

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
