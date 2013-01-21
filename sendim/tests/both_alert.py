"""
Test to create alerts for a service status and host status.
"""

from django.utils import unittest
from django.utils.timezone import now

from referentiel.models import Host, Service, Status, Reference
from sendim.models import Alert, Event

from datetime import timedelta

class Host_and_service(unittest.TestCase):
    """
    Try to firstly create an host DOWN alert,
    and after an service alert for this host.
    Test if both alerts have the same Event.
    """
    def setUp(self):
	self.host = Host.objects.create(name='host1')
	self.service = Service.objects.create(name='host1')
        self.h_alert = Alert.objects.create(host=self.host,service=self.service,status=Status.objects.get(pk=4),date=now(),info='Test - host alert')
        self.s_alert = Alert.objects.create(host=self.host,service=self.service,status=Status.objects.get(pk=1),date=now()+timedelta(0,3),info='Test - service alert')
        self.events = list()

    def tearDown(self):
	self.host.delete()
	self.service.delete()
        [ A.delete() for A in Alert.objects.all() ]
        [ E.delete() for E in Event.objects.all() ]

    def test_auto_aggregation(self):
        """
        Test if an first host alert and a second service alert
        will be linked in a same Event.
        """
        for A in Alert.objects.filter(event=None):
            E = A.link()
            if not E in self.events : self.events.append(E)
        for E in self.events :
            self.assertIsInstance(E, Event)
        self.assertEqual(Event.objects.count(),1)
        
class Service_and_host(unittest.TestCase):
    """
    Try to firstly create an service WARNING alert,
    and after an host DOWN alert.
    Test if both alerts have the same Event.
    """
    def setUp(self):
	self.host = Host.objects.create(name='host1')
	self.service = Service.objects.create(name='host1')
        self.h_alert = Alert.objects.create(host=self.host,service=self.service,status=Status.objects.get(pk=4),date=now()+timedelta(0,3),info='Test - host alert')
        self.s_alert = Alert.objects.create(host=self.host,service=self.service,status=Status.objects.get(pk=1),date=now(),info='Test - service alert')
        self.events = list()

    def tearDown(self):
	self.host.delete()
	self.service.delete()
        [ A.delete() for A in Alert.objects.all() ]
        [ E.delete() for E in Event.objects.all() ]

    def test_auto_aggregation(self):
        """
        Test if an first host alert and a second service alert
        will be linked in a same Event.
        """
        for A in Alert.objects.filter(event=None):
            E = A.link()
            if not E in self.events : self.events.append(E)
        for E in self.events :
            self.assertIsInstance(E, Event)
        self.assertEqual(Event.objects.count(),1)
        
