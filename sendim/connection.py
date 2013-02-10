from django.conf import settings
from socket import SocketType,error,gaierror

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
