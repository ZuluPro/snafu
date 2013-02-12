from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.utils import IntegrityError

from referentiel.models import *
from sendim.models import *
from sendim.glpi_manager import GLPI_manager
from sendim.exceptions import UnableToConnectGLPI

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
sh.setFormatter(formatter)
logger.addHandler(sh)

GLPI_manager = GLPI_manager()

def colorize(string='', color='default') :
    colors = {
        'default' : "0",
        'red' : "0;31",
        'green' : "0;32",
        'yellow' : "0;33",
        'pink' : "0;35"
    }
    return '\033['+colors[color]+'m'+string+'\033[0m'

class Command(BaseCommand) :
    args = None
    def handle(self, *args, **options) :

        if not MailTemplate.objects.filter(chosen=True).exists() :
            if not MailTemplate.objects.all().exists() :
                M = MailTemplate.objects.get(pk=1)
                M.chosen = True
                M.save()

        try :
            for host in GLPI_manager.list('computer') :
                try :
                    if 'name' in host :
                        H = Host.objects.create(
                          name=host['name'],
                          glpi_id=host['id'],
                          host_type='computer'
                        )
                        logger.info('Add computer : "'+H.name +'"')
                except IntegrityError :
					logger.warning('Computer "' +host['name']+ '" already exists')

            for host in GLPI_manager.list('networkequipment') :
                try :
                    if 'name' in host :
                        H = Host.objects.create(
                          name=host['name'],
                          glpi_id=host['id'],
                          host_type='networkequipment'
                        )
                        logger.info('Add computer : "'+H.name +'"')
                except IntegrityError :
					logger.warning('Computer "' +host['name']+ '" already exists')

#            for host in get_hosts_from_glpi() :
#                try:
#                    H = Host(host=host['name'], glpi_id=host['id'], host_type='networkequipment' )
#                    H.save()
#                    logprint('Add network equipement '+H.host, 'green')
#                except IntegrityError : logprint('Network equipement ' +H.host+ ' already exists', 'yellow')

            for user in GLPI_manager.list('user') :
                try:
                    GU = GlpiUser.objects.create(
                      name=user['name'].encode('latin-1').decode('utf-8'),
                      glpi_id=user['id']
                    )
                    logger.info('Add GLPI user : '+GU.name)
                except IntegrityError :
					logger.warning('User "' +user['name']+ '" already exists')

            for group in GLPI_manager.list('group') :
                try:
                    GG = GlpiGroup.objects.create(
                      name=group['name'].encode('latin-1').decode('utf-8'),
                      glpi_id=group['id']
                    )
                    logger.info('Add GLPI group : '+GG.name)
                except IntegrityError :
					logger.warning('Group "' +group['name']+ '" already exists')

            for supplier in GLPI_manager.list('supplier') :
                try:
                    S = GlpiSupplier.objects.create(
                      name=supplier['name'].encode('latin-1').decode('utf-8'),
                      glpi_id=user['id']
                    )
                    logger.info('Add GLPI supplier : "' +supplier['name']+ '"')
                except IntegrityError :
					logger.warning('Supplier "' +supplier['name']+ '" already exists')

            for category in GLPI_manager.list('ITILCategory') :
                try:
                    C = GlpiCategory.objects.create(
                      name=category['name'].encode('latin-1').decode('utf-8'),
                      glpi_id=user['id']
                    )
                    logger.info('Add GLPI ITIL category : "' +category['name']+ '"')
                except IntegrityError :
					logger.warning('Category "' +category['name']+ '" already exists')

        except UnableToConnectGLPI, e :
            logger.info('Impossible to connect to GLPI : '+str(e.message))
