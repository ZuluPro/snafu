from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.utils import IntegrityError

from referentiel.models import *
from sendim.models import *
from sendim.defs import get_hosts_from_glpi#, get_users_from_glpi, get_groups_from_glpi

from common import logprint

class Command(BaseCommand) :
    args = None
    def handle(self, *args, **options) :

        if MailTemplate.objects.filter(choosen=True).exists() :
            M = MailTemplate.objects.get(pk=1)
            M.choosen = True
            M.save()

        for host in get_hosts_from_glpi() :
                try:
                        H = Host(host=host['name'], glpi_id=host['id'], host_type='computer' )
                        H.save()
			logprint('Add computer : '+H.host, 'green')
                except IntegrityError : logprint('Computer ' +H.host+ ' already exists', 'yellow')

        for host in get_hosts_from_glpi() :
                try:
                        H = Host(host=host['name'], glpi_id=host['id'], host_type='networkequipment' )
                        H.save()
			logprint('Add network equipement '+H.host, 'green')
                except IntegrityError : logprint('Network equipement ' +H.host+ ' already exists', 'yellow')

#        for user in get_users_from_glpi() :
#                try:
#                        GU = GlpiUser(glpi_user=user['name'], glpi_id=user['id'] )
#                        GU.save()	
#			logprint('Add GLPI user : '+GU.glpi_user, 'green')
#                except IntegrityError : logprint('User ' +GU.glpi_user+ ' already exists', 'yellow')
#
#        for group in get_groups_from_glpi() :
#            group['name'] = group['name'].replace(u'\xc3\xa9', u'\xe9')
#            group['name'] = group['name'].replace(u'\xc3\xa8', u'\xe8')
#
#            try:
#                H = GlpiGroup(glpi_group=group['name'], glpi_id=group['id'] )
#                H.save()	
#		logprint('Add GLPI group : '+GU.glpi_group, 'green')
#            except IntegrityError : logprint('Group ' +GU.glpi_group+ ' already exists', 'yellow')
