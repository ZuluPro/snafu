from django.conf import settings

import xmlrpclib
from urllib2 import HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler, build_opener, install_opener, URLError

from socket import SocketType,error,gaierror
from urlparse import urlsplit

glpiServer = xmlrpclib.Server(settings.SNAFU['glpi-xmlrpc'], verbose=False, allow_none=True)

def doLogin():
    try :
       loginInfo = glpiServer.glpi.doLogin({
           'login_name':settings.SNAFU['glpi-login'],
           'login_password':settings.SNAFU['glpi-password']
       } )
    except (error,gaierror), e: 
       loginInfo = {'error':e}
    return loginInfo 

def doLogout():
    glpiServer.glpi.doLogout()

def checkGlpi():
    S = SocketType()
    S.settimeout(2)
    try : 
        glpiStatus = S.connect_ex( ( urlsplit(settings.SNAFU['glpi-url']).netloc, 80 ) )
        S.close()
    except (error,gaierror), e : glpiStatus = e
    return glpiStatus

def checkSmtp():
    try : 
        S = SocketType()
        S.settimeout(2)
        smtpStatus = S.connect_ex( ( settings.SNAFU['smtp-server'],settings.SNAFU['smtp-port']) )
        S.close()
    except (error,gaierror), e : smtpStatus = e
    return smtpStatus

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
        opener.open(settings.SNAFU['nagios-url'], timeout=2)
        nagiosStatus = False 
    except (error,gaierror,URLError), e : 
        nagiosStatus = e
    return nagiosStatus
