from django.conf import settings

class UnableToConnectGLPI(Exception):
    "Unable to connect to GLPI webservice : "+settings.SNAFU['glpi-url']
    pass

class UnableToConnectNagios(Exception):
    """Unable to connect to Nagios website."""
    pass

class UnableToConnectSMTP(Exception):
    """Unable to connect to SMTP server."""
    pass
