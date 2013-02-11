"""
"""

from django.utils import unittest
from django.core import management

from referentiel.models import Translation
from sendim.models import Alert, Event
from sendim.tests.defs import create_alert

class Translation_TestCase(unittest.TestCase):
	"""
	"""
	def setUp(self):
		management.call_command('loaddata', 'test_host.json', database='default', verbosity=0)
		management.call_command('loaddata', 'test_translation.json', database='default', verbosity=0)
		self.alert = create_alert(host='test host',service='test service',status='WARNING')

	def tearDown(self):
		Alert.objects.all().delete()
		Event.objects.all().delete()

	def test_find_translation(self):
		self.alert.find_translation()
		self.assertIsNotNone(self.alert.translation)

	def test_event_creation(self):
		self.alert.link()
		self.assertIsNotNone(self.alert.event)
		self.assertNotEqual(self.alert.event.message, self.alert.info)

	def test_event_creation_without(self):
		Translation.objects.get(pk=1).delete()
		self.alert.link()
		self.assertIsNotNone(self.alert.event)
		self.assertNotEqual(self.alert.event.message, 'Test translation')
