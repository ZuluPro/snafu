SNAFU = {
    'nagios-url': 'http://zulunagios/',
    'nagios-status': 'http://zulunagios/cgi-bin/nagios3/status.cgi',
    'nagios-history': 'http://zulunagios/cgi-bin/nagios3/history.cgi',
    'nagios-login': 'nagiosadmin',
    'nagios-password': 'deadkill',
    'glpi-url':'http://zuluglpi/glpi/',
    'glpi-xmlrpc':'http://zuluglpi/glpi/plugins/webservices/xmlrpc.php',
    'glpi-login':'glpi',
    'glpi-password':'glpi',
    'smtp-from':"snafu.django@gmail.com",
    'smtp-password':"deadkill",
    'smtp-server':'smtp.gmail.com',
    'smtp-port':587
}

BASEDIR = "/home/www-data"

INTERNAL_IPS = ('10.0.0.225',)

LOGIN_URL = '/snafu/login'

TEMPLATE_DIRS = (BASEDIR+ '/snafu/sendim/templates/',)
