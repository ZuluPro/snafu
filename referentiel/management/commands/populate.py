from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.utils import IntegrityError

from referentiel.models import *
from sendim.models import *

import xmlrpclib
from common import logprint


serverUrl = settings.SNAFU['glpi-xmlrpc']
loginData = { 'login_name':settings.SNAFU['glpi-login'], 'login_password':settings.SNAFU['glpi-password'] }
ws = xmlrpclib.Server(serverUrl, verbose=False, allow_none=True)
ws_session = ws.glpi.doLogin(loginData)

class Command(BaseCommand) :
    args = None
    def handle(self, *args, **options) :

	if not MailTemplate.objects.all() :
		MailTemplate(
			subject='[ Incident $MAIL_TYPE$ - $CRITICITY$ ] $DATE$ - $MESSAGE$ sur $HOST$ - GLPI $GLPI$',
			body=u"Bonjour,\nNos syst\xe8mes de supervision ont d\xe9t\xe9ct\xe9 une anomalie sur l'\xe9quipement $HOST$ le $JOUR$ \xe0 $HEURE$ : $TRADUCTION$\n\nUn ticket d'incident a \xe9t\xe9 ouvert au lien suivant :\n$GLPI-URL$$GLPI$\n\nLog Nagios correspondant :\n$LOG$\n\nCordialement,",
			choosen=True
		).save()
		logprint('Add first mail template')

        computers = ws.glpi.listObjects( { 'session': ws_session['session'], 'itemtype': 'computer', 'limit': 2000 } )
        for host in computers :
                try:
                        H = Host(host=host['name'], glpi_id=host['id'], host_type='computer' )
                        H.save()
			logprint('Add computer : '+H.host, 'green')
                except IntegrityError : logprint('Computer ' +H.host+ ' already exists', 'yellow')

        netcomputers = ws.glpi.listObjects( { 'session': ws_session['session'], 'itemtype': 'networkequipment', 'limit': 2000 } )
        for host in netcomputers :
                try:
                        H = Host(host=host['name'], glpi_id=host['id'], host_type='networkequipment' )
                        H.save()
			logprint('Add network equipement '+H.host, 'green')
                except IntegrityError : logprint('Network equipement ' +H.host+ ' already exists', 'yellow')

        for user in ws.glpi.listUsers( { 'session': ws_session['session'] } ) :
                try:
                        GU = GlpiUser(glpi_user=user['name'], glpi_id=user['id'] )
                        GU.save()	
			logprint('Add GLPI user : '+GU.glpi_user, 'green')
                except IntegrityError : logprint('User ' +GU.glpi_user+ ' already exists', 'yellow')

        for group in ws.glpi.listGroups( { 'session': ws_session['session'] } ) :
            group['name'] = group['name'].replace(u'\xc3\xa9', u'\xe9')
            group['name'] = group['name'].replace(u'\xc3\xa8', u'\xe8')

            try:
                H = GlpiGroup(glpi_group=group['name'], glpi_id=group['id'] )
                H.save()	
		logprint('Add GLPI group : '+GU.glpi_group, 'green')
            except IntegrityError : logprint('Group ' +GU.glpi_group+ ' already exists', 'yellow')
