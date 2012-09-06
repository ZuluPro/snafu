from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from django.db.utils import IntegrityError

from referentiel.models import *

from common import logprint
import os,sys,re
import sqlite3
import xmlrpclib


serverUrl = settings.SENDIM['glpi-url']
loginData = { 'login_name':settings.SENDIM['glpi-login'], 'login_password':settings.SENDIM['glpi-password'] }
ws = xmlrpclib.Server(serverUrl, verbose=False, allow_none=True)
ws_session = ws.glpi.doLogin(loginData)

impact = { 'Bas':2, 'Moyen':3, 'Haut':4, u'Tr\xe8s haut':5 }
urgency = { 'Basse':2, 'Moyenne':3, 'Haute':4, u'Tr\xe8s haute':5 }
                                
class Command(BaseCommand) :
    args = None
    def handle(self, *args, **options) :

        computers = ws.glpi.listObjects( { 'session': ws_session['session'], 'itemtype': 'computer', 'limit': 2000 } )
        for host in computers :
                try:
                        H = Host(host=host['name'], glpi_id=host['id'], host_type='computer' )
                        H.save()
			print logprint('Add computer : '+H.host, 'green')
                except IntegrityError : print logprint('Computer ' +H.host+ ' already exists', 'yellow')

        netcomputers = ws.glpi.listObjects( { 'session': ws_session['session'], 'itemtype': 'networkequipment', 'limit': 2000 } )
        for host in netcomputers :
                try:
                        H = Host(host=host['name'], glpi_id=host['id'], host_type='networkequipment' )
                        H.save()
			print logprint('Add network equipement '+H.host, 'green')
                except IntegrityError : print logprint('Network equipement ' +H.host+ ' already exists', 'yellow')

        for user in ws.glpi.listUsers( { 'session': ws_session['session'] } ) :
                try:
                        GU = GlpiUser(glpi_user=user['name'], glpi_id=user['id'] )
                        GU.save()	
			print logprint('Add GLPI user : '+GU.glpi_user, 'green')
                except IntegrityError : print logprint('User ' +GU.glpi_user+ ' already exists', 'yellow')

        for group in ws.glpi.listGroups( { 'session': ws_session['session'] } ) :
            group['name'] = group['name'].replace(u'\xc3\xa9', u'\xe9')
            group['name'] = group['name'].replace(u'\xc3\xa8', u'\xe8')

            try:
                H = GlpiGroup(glpi_group=group['name'], glpi_id=group['id'] )
                H.save()	
		print logprint('Add GLPI group : '+GU.glpi_group, 'green')
            except IntegrityError : print logprint('Group ' +GU.glpi_group+ ' already exists', 'yellow')

        for status in ['WARNING','CRITICAL','OK', 'DOWN','UP', 'UNKNOWN' ] :
                try:
                        S = Status(status=status)
                        S.save()
                except IntegrityError : pass

        for urg in urgency :
                try:
                        H = GlpiUrgency(glpi_urgency=urg, glpi_id=urgency[urg] )
                        H.save()
                except IntegrityError : pass

        for imp in impact :
                try:
                        H = GlpiImpact(glpi_impact=imp, glpi_id=impact[imp] )
                        H.save()
                except IntegrityError : pass
                
        for prio in urgency :
                try:
                        H = GlpiPriority(glpi_priority=prio, glpi_id=urgency[prio] )
                        H.save()
                except IntegrityError : pass

        for criticity in ['Mineur','Majeur'] :
                try:
                        C = MailCriticity(mail_criticity=criticity)
                        C.save()	
                except IntegrityError : pass

#        for cat in categories :
#                try:
#                        H = GlpiCategory(glpi_category=cat, glpi_id=categories[cat] )
#                        H.save()	
#                except : pass

#        for sup in suppliers :
#                try:
#                        H = GlpiSupplier(glpi_supplier=sup, glpi_id=suppliers[sup] )
#                        H.save()	
#                except : pass
