DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    'NAME': 'test_snafu_db',    # Or path to database file if using sqlite3.
    'USER': '', # Not used with sqlite3.
    'PASSWORD': '',     # Not used with sqlite3.
    'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
    'PORT': '', # Set to empty string for default. Not used with sqlite3.
  }
}

SNAFU = {
   'glpi-url':'http://test-glpi/glpi/',
   'glpi-xmlrpc':'http://test-glpi/glpi/plugins/webservices/xmlrpc.php',
   'glpi-login':'glpi',
   'glpi-password':'glpi',
   'smtp-from':"you@yours.com",
   'smtp-password':"password",
   'smtp-server':'smtp.yours.com',
   'smtp-port':25
}

BROKER_BACKEND = 'memory'
