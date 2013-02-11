"""
Test to create alerts for a service status and host status.
"""

from django.utils import unittest
from django.core import management

from sendim.models import Alert, Event
from sendim.tests.defs import create_alert, create_alert_from

class Host_and_service(unittest.TestCase):
	"""
	Try to firstly create an host DOWN alert,
	and after an service alert for this host.
	Test if both alerts have the same Event.
	"""
	def setUp(self):
		management.call_command('loaddata', 'test_host.json', database='default', verbosity=0)
		self.h_alert = create_alert(host='test host', service='Host status', status='DOWN')
		self.h_alert.save()
		self.s_alert = create_alert_from(self.h_alert, service='test service', status='WARNING') 
		self.s_alert.save()

	def tearDown(self):
		Alert.objects.all().delete()
		Event.objects.all().delete()

	def test_auto_aggregation(self):
		"""
		Test if an first host alert and a second service alert
		will be linked in a same Event.
		"""
		for A in Alert.objects.filter(event=None):
			E = A.link()
		self.assertEqual(Event.objects.count(),1)
		
class Service_and_host(unittest.TestCase):
	"""
	Try to firstly create an service WARNING alert,
	and after an host DOWN alert.
	Test if both alerts have the same Event.
	"""
	def setUp(self):
		management.call_command('loaddata', 'test_host.json', database='default', verbosity=0)
		self.s_alert = create_alert(host='test host', service='test service', status='WARNING') 
		self.s_alert.save()
		self.h_alert = create_alert_from(self.s_alert, service='Host status', status='DOWN')
		self.h_alert.save()

	def tearDown(self):
		Alert.objects.all().delete()
		Event.objects.all().delete()

	def test_auto_aggregation(self):
		"""
		Test if an first host alert and a second service alert
		will be linked in a same Event.
		"""
		for A in Alert.objects.filter(event=None):
			E = A.link()
		self.assertEqual(Event.objects.count(),2)
		
