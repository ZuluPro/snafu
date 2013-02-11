"""
Test to create alerts for host status (DOWN/UP).
"""

from django.utils import unittest
from django.core import management

from referentiel.models import Host, Service, Status, Reference
from sendim.models import Alert, Event
from sendim.tests.defs import create_alert

class SingleHost_SingleAlert_TestCase(unittest.TestCase):
	"""
	Tests for a single Host Status DOWN.
	"""
	def setUp(self):
		management.call_command('loaddata', 'test_host.json', database='default', verbosity=0)
		self.alert = create_alert(host='test host', service='test service')
		self.alert.save()
		self.events = list()

	def tearDown(self):
		Alert.objects.all().delete()
		[ E.delete() for E in self.events ]

	def test_alert_link_to_event(self):
		"""Try to link alert to an Event."""
		for A in Alert.objects.filter(event=None) :
			E = A.link()
			if not E in self.events : self.events.append(E)
		for E in self.events :
			self.assertIsInstance(E, Event)
		self.assertEqual(Event.objects.count(),1)

	def test_create_glpi_ticket(self):
		"""Try to create glpi ticket."""
		self.events.append(self.alert.link())
		ticket_id = self.events[0].create_ticket()
		self.assertIsInstance(int(ticket_id), int)

	def test_close_event(self):
		"""
		Try to close the event.
		Normally it can't do.
		"""
		self.events.append(self.alert.link())
		self.events[0].close()
		self.assertFalse(self.events[0].closed)


class SingleHost_MultipleAlert_TestCase(unittest.TestCase):
	"""
	Tests for 2 Alerts DOWN and UP.
	"""
	def setUp(self):
		management.call_command('loaddata', 'test_host.json', database='default', verbosity=0)
		self.alert1 = create_alert(host='test host', service='Host status')
		self.alert1.save()
		self.alert2 = create_alert(host='test host', service='Host status', isDown=False)
		self.alert2.save()
		self.events = list()

	def tearDown(self):
		Alert.objects.all().delete()
		[ E.delete() for E in self.events ]

	def test_alert_link_to_event(self):
		"""Try to link alerts to a single Event."""
		for A in Alert.objects.filter(event=None) :
			E = A.link()
			if not E in self.events : self.events.append(E)
		for E in self.events :
			self.assertIsInstance(E, Event)
		self.assertEqual(Event.objects.count(),1)

	def test_create_glpi_ticket(self):
		"""Try to create glpi ticket."""
		for A in Alert.objects.filter(event=None) :
			E = A.link()
			if not E in self.events : self.events.append(E)

		for E in self.events :
			ticket_id = E.create_ticket()
			self.assertIsInstance(int(ticket_id), int)

	def test_close_event(self):
		"""
		Try to close the event.
		Normally it can.
		"""
		for A in Alert.objects.filter(event=None) :
			E = A.link()
			if not E in self.events : self.events.append(E)
		self.events[0].close()
		self.assertTrue(self.events[0].closed)


