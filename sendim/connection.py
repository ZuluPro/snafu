from django.conf import settings

import xmlrpclib
from urllib2 import HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler, build_opener, install_opener
from socket import error

glpiServer = xmlrpclib.Server(settings.SNAFU['glpi-xmlrpc'], verbose=False, allow_none=True)

def doLogin():
    try :
       loginInfo = glpiServer.glpi.doLogin({
           'login_name':settings.SNAFU['glpi-login'],
           'login_password':settings.SNAFU['glpi-password']
       } )
    except error, e: 
       loginInfo = {'error':e}
    return loginInfo 

def doLogout():
    glpiServer.glpi.doLogout()

def checkSmtp():
    S = socket.SocketType()
    smtpStatus = S.connect_ex( ( settings.SNAFU['smtp-server'],settings.SNAFU['smtp-port']) )

def getOpener():
    www = settings.SNAFU['nagios-url']
    username = settings.SNAFU['nagios-login']
    password = settings.SNAFU['nagios-password']
    
    passman = HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, www, username, password)
    authhandler = HTTPBasicAuthHandler(passman)
    opener = build_opener(authhandler)
    install_opener(opener)
    return opener

def checkNagios():
    opener = getOpener()
    try :
        opener.open(settings.SNAFU['nagios-url'])
        nagiosStatus = False 
    except error, e : 
        nagiosStatus = e
    print nagiosStatus
    return nagiosStatus
