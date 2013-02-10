from django.conf import settings

import xmlrpclib

from socket import SocketType,error,gaierror
from urlparse import urlsplit

glpiServer = xmlrpclib.Server(settings.SNAFU['glpi-xmlrpc'], verbose=False, allow_none=True)

def doLogin():
    """
	Make login on GLPI webservice.
    Return loginInfo.
	"""
    try :
       loginInfo = glpiServer.glpi.doLogin({
           'login_name':settings.SNAFU['glpi-login'],
           'login_password':settings.SNAFU['glpi-password']
       } )
    except (error,gaierror), e: 
       loginInfo = {'error':e}
    return loginInfo 

def doLogout():
    """Make logout on GLPI webservice."""
    glpiServer.glpi.doLogout()

def checkGlpi():
    """
	Make a connection socket test into GLPI webserver.
    Return status code of SocketType.connect_ex().
	"""
    S = SocketType()
    S.settimeout(2)
    try : 
        glpiStatus = S.connect_ex( ( urlsplit(settings.SNAFU['glpi-url']).netloc, 80 ) )
        S.close()
    except (error,gaierror), e : glpiStatus = e
    return glpiStatus

def checkSmtp():
    """
	Make a connection socket test into STMP server.
    Return status code of SocketType.connect_ex().
	"""
    try : 
        S = SocketType()
        S.settimeout(2)
        smtpStatus = S.connect_ex( ( settings.SNAFU['smtp-server'],settings.SNAFU['smtp-port']) )
        S.close()
    except (error,gaierror), e : smtpStatus = e
    return smtpStatus
