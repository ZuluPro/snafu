from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.utils import IntegrityError

from referentiel.models import *
from sendim.models import *
from sendim.glpi_manager import GLPI_manager
from sendim.exceptions import UnableToConnectGLPI

from common import logprint
GLPI_manager = GLPI_manager()

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
                        logprint('Add computer : "'+H.name +'"', 'green')
                except IntegrityError : logprint('Computer ' +host['name']+ ' already exists', 'yellow')

            for host in GLPI_manager.list('networkequipment') :
                try :
                    if 'name' in host :
                        H = Host.objects.create(
                          name=host['name'],
                          glpi_id=host['id'],
                          host_type='networkequipment'
                        )
                        logprint('Add computer : "'+H.name +'"', 'green')
                except IntegrityError : logprint('Computer ' +host['name']+ ' already exists', 'yellow')

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
                    logprint('Add GLPI user : '+GU.name, 'green')
                except IntegrityError : logprint('User "' +user['name']+ '" already exists', 'yellow')

            for group in GLPI_manager.list('group') :
                try:
                    GG = GlpiGroup.objects.create(
                      name=group['name'].encode('latin-1').decode('utf-8'),
                      glpi_id=group['id']
                    )
                    logprint('Add GLPI group : '+GG.name, 'green')
                except IntegrityError : logprint('Group "' +group['name']+ '" already exists', 'yellow')

            for supplier in GLPI_manager.list('supplier') :
                try:
                    S = GlpiSupplier.objects.create(
                      name=supplier['name'].encode('latin-1').decode('utf-8'),
                      glpi_id=user['id']
                    )
                    logprint('Add GLPI supplier : "' +supplier['name']+ '"', 'green')
                except IntegrityError : logprint('Supplier "' +supplier['name']+ '" already exists', 'yellow')

            for category in GLPI_manager.list('ITILCategory') :
                try:
                    C = GlpiCategory.objects.create(
                      name=category['name'].encode('latin-1').decode('utf-8'),
                      glpi_id=user['id']
                    )
                    logprint('Add GLPI ITIL category : "' +category['name']+ '"', 'green')
                except IntegrityError : logprint('Category "' +category['name']+ '" already exists', 'yellow')

        except UnableToConnectGLPI, e :
            logprint('Impossible to connect to GLPI : '+str(e.message), 'red')
