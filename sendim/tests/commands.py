from django.utils import unittest
from django.core import management
from django.conf import settings

from referentiel.models import Host, Service, GlpiUser, GlpiGroup, GlpiSupplier, GlpiCategory
from sendim.models import Alert, Event
from sendim.tests.defs import internet_is_on

from os.path import join
import logging
logging.disable(logging.CRITICAL)


class Commands_TestCase(unittest.TestCase):
	"""
	Tests commands in "referentiel/management/commands/".
	"""
	def setUp(self):
		pass

	def tearDown(self):
		Host.objects.all().delete()
		GlpiUser.objects.all().delete()
		GlpiGroup.objects.all().delete()
		GlpiSupplier.objects.all().delete()
		GlpiCategory.objects.all().delete()
		Alert.objects.all().delete()
		Event.objects.all().delete()

	def test_populate(self):
		management.call_command('populate', database='default', verbosity=0)

#	@unittest.skipIf(not internet_is_on(), 'No internet connection available.')
#	def test_reload_alerts(self):
#		management.call_command('loaddata', 'test_supervisor', database='default', verbosity=0)
#		management.call_command('reload_alerts', database='default', verbosity=0)

#class XML_Clients_TestCase(unittest.TestCase):
#
#	def setUp(self):
#		pass
#
#	def test_push_alert_py(self):
#		from commands import getstatusoutput as cmd
#
#
