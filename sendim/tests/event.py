"""
"""

from django.utils import unittest
from django.core import management

from sendim.models import Alert, Event
from sendim.tests.defs import create_event, create_alert

class Event_TestCase(unittest.TestCase):
	"""
	"""
	def setUp(self):
		management.call_command('loaddata', 'test_supervisor.json', database='default', verbosity=0)
		management.call_command('loaddata', 'test_host.json', database='default', verbosity=0)

		self.event1 = create_event(create_alert(host='test host'), message='Aggregation Event#1', criticity='Mineur', glpi=10, mail=True)
		self.event1.save()
		
		self.event2 = create_event(create_alert(host='test host2'), message='Aggregation Event#2', criticity='?')
		self.event2.save()

	def tearDown(self):
		Event.objects.all().delete()
		Alert.objects.all().delete()

	def test_aggregation_into_treated(self):
		"""
		Aggregate two events. One of both is treated,
		so the event must hold his fields.
		"""
		# Test if event hold his field
		self.event1 = self.event1.aggregate([self.event2.pk])
		self.assertEqual(self.event1.get_alerts().count(), 10)
		self.assertEqual(self.event1.glpi, 10)
		self.assertEqual(self.event1.criticity, self.event1.criticity)
		self.assertTrue(self.event1.mail)

	def test_aggregation_into_not_treated(self):
		"""
		Aggregate two events. One of both is treated,
		so the event must hold his fields.
		"""
		# Test if event hold his field
		self.event2 = self.event2.aggregate([self.event1.pk])
		self.assertEqual(self.event2.get_alerts().count(), 10)
		self.assertEqual(self.event2.glpi, 10)
		self.assertEqual(self.event2.criticity, self.event1.criticity)
		self.assertTrue(self.event2.mail)
