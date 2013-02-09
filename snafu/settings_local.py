from django.conf import settings
INSTALLED_APPS = settings.INSTALLED_APPS

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql' or 'oracle'.
        'NAME': 'snafu_db',
        'USER': 'zulu',
        'PASSWORD': 'zulu',
        'HOST': '',
        'PORT': '',
    }
}

SECRET_KEY = 'd4(75&amp;+hq7bal9#km801^u1#d$3*yvgfvs9d!!%f!i9yw^jrc4'

# SNAFU settings
SNAFU = {
    'glpi-url':'http://yourglpi/glpi/',
    'glpi-xmlrpc':'http://yourglpi/glpi/plugins/webservices/xmlrpc.php',
    'glpi-login':'glpi',
    'glpi-password':'glpi',
    'smtp-from':"you@yours.com",
    'smtp-password':"password",
    'smtp-server':'smtp.yours.com',
    'smtp-port':25
}

if 'djcelery' in INSTALLED_APPS :
    # RabbitMQ settings
    BROKER_HOST = "localhost"
    BROKER_PORT = 5672
    BROKER_USER = "snafu"
    BROKER_PASSWORD = "snafu"
    BROKER_VHOST = "snafu"
    #BROKER_BACKEND = 'memory'
    #BROKER_URL = 'amqp://snafu@localhost:5672/'

    TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'

# Debug Tool Bar
#INSTALLED_APPS = INSTALLED_APPS+('debug_toolbar',)
#if 'debug_toolbar' in INSTALLED_APPS :
#    INTERNAL_IPS = ('10.0.0.225',)
#    MIDDLEWARE_CLASSES = settings.MIDDLEWARE_CLASSES+('debug_toolbar.middleware.DebugToolbarMiddleware',)

# Django Extensions
#INSTALLED_APPS = INSTALLED_APPS+('django_extensions',)

