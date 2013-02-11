"""
Test to create alerts for service status (WARNING/CRITICAL/OK).
"""

from django.utils import unittest
from django.core import management

from referentiel.models import Service, Status
from sendim.models import Alert, Event
from sendim.tests.defs import create_alert, create_alert_from

class SingleService_SingleAlert_TestCase(unittest.TestCase):
	"""
	Tests for a single WARNING alert.
	"""
	def setUp(self):
		management.call_command('loaddata', 'test_host.json', database='default', verbosity=0)
		self.alert = create_alert(host='test host',service='test service',status=Status.objects.get(pk=1))
		self.events = list()

	def tearDown(self):
		Alert.objects.all().delete()
		Event.objects.all().delete()

	def test_alert_link_to_event(self):
		"""Try to link alert to an Event."""
		self.events.append(self.alert.link())
		self.assertIsInstance(self.events[0], Event)

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

class SingleService_MultipleAlert_TestCase(unittest.TestCase):
	"""
	Tests for 3 Alerts (WARNING/CRITICAL/OK)..
	"""
	def setUp(self):
		management.call_command('loaddata', 'test_host.json', database='default', verbosity=0)
		self.events = list()
		self.alert1 = create_alert(host='test host',service='test service')
		self.alert1.save()
		self.alert2 = create_alert_from(self.alert1)
		self.alert2.save()
		self.alert3 = create_alert_from(self.alert2, isDown=False)
		self.alert3.save()

	def tearDown(self):
		Alert.objects.all().delete()
		Event.objects.all().delete()

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

class MultipleService_MultipleAlert_TestCase(unittest.TestCase):
	"""
	Tests for 2 Events of 3 Alerts (WARNING/CRITICAL/OK).
	"""
	def setUp(self):
		management.call_command('loaddata', 'test_host.json', database='default', verbosity=0)
		self.service1 = Service.objects.create(name='test service1')
		self.service2 = Service.objects.create(name='test service2')
		self.events = list()

		self.alert1 = create_alert(host='test host',service='test service1')
		self.alert1.save()
		self.alert2 = create_alert_from(self.alert1)
		self.alert2.save()
		self.alert3 = create_alert_from(self.alert2, isDown=False)
		self.alert3.save()

		self.alert4 = create_alert(host='test host',service='test service2')
		self.alert4.save()
		self.alert5 = create_alert_from(self.alert1)
		self.alert5.save()
		self.alert6 = create_alert_from(self.alert2, isDown=False)
		self.alert6.save()

	def tearDown(self):
		Service.objects.all().delete()
		Alert.objects.all().delete()
		Event.objects.all().delete()

	def test_alert_link_to_event(self):
		"""Try to link alert to 2 Events."""
		for A in Alert.objects.filter(event=None) :
			E = A.link()
			if not E in self.events : self.events.append(E)
		for E in self.events :
			self.assertIsInstance(E, Event)
		self.assertEqual(Event.objects.count(),2)

	def test_create_glpi_ticket(self):
		"""Try to create 2 glpi ticket."""
		for A in Alert.objects.filter(event=None) :
			E = A.link()
			if not E in self.events : self.events.append(E)

		for E in self.events :
			ticket_id = E.create_ticket()
			self.assertIsInstance(int(ticket_id), int)
