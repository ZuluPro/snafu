"""
"""

from django.utils import unittest
from django.core import management

from referentiel.models import Reference
from sendim.models import Alert, Event
from sendim.tests.defs import create_alert

class Reference_TestCase(unittest.TestCase):
	"""
	"""
	def setUp(self):
		management.call_command('loaddata', 'test_host.json', database='default', verbosity=0)
		management.call_command('loaddata', 'test_reference.json', database='default', verbosity=0)
		self.alert = create_alert(host='test host', service='test service', status='WARNING')

	def tearDown(self):
		Event.objects.all().delete()
		Alert.objects.all().delete()

	def test_find_reference(self):
		""""""
		self.alert.find_reference()
		self.assertIsNotNone(self.alert.reference)

	def test_event_creation(self):
		self.alert.link()
		self.assertIsNotNone(self.alert.event)
		self.assertNotEqual(self.alert.event.criticity, '?')

	def test_event_creation_without(self):
		Reference.objects.get(pk=1).delete()
		self.alert.link()
		self.assertIsNotNone(self.alert.event)
		self.assertEqual(self.alert.event.criticity, '?')
