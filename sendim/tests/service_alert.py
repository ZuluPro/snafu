"""
Test to create alerts for service status (WARNING/CRITICAL/OK).
"""

from django.utils import unittest
from django.utils.timezone import now

from referentiel.models import Host, Service, Status, Reference
from sendim.models import Alert, Event

from datetime import datetime, timedelta

class SingleService_SingleAlert_TestCase(unittest.TestCase):
    """
    Tests for a single WARNING alert.
    """
    def setUp(self):
	self.host = Host.objects.create(name='host1')
	self.service = Service.objects.create(name='host1')
        self.alert = Alert.objects.create(host=self.host,service=self.service,status=Status.objects.get(pk=1),date=now(),info='Test alert')
        self.events = list()

    def tearDown(self):
	self.host.delete()
	self.service.delete()
        [ A.delete() for A in Alert.objects.all() ]
        [ E.delete() for E in Event.objects.all() ]

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
	self.host = Host.objects.create(name='host1')
	self.service = Service.objects.create(name='service1')
        self.events = list()
        self.alert1 = Alert.objects.create(host=self.host,service=self.service,status=Status.objects.get(pk=1),date=now(),info='Test alert WARNING')
        self.alert2 = Alert.objects.create(host=self.host,service=self.service,status=Status.objects.get(pk=2),date=now()+timedelta(0,3),info='Test alert CRITICAL')
        self.alert3 = Alert.objects.create(host=self.host,service=self.service,status=Status.objects.get(pk=5),date=now()+timedelta(0,6),info='Test alert OK')

    def tearDown(self):
	self.host.delete()
	self.service.delete()
        [ A.delete() for A in Alert.objects.all() ]
        [ E.delete() for E in Event.objects.all() ]

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
	self.host = Host.objects.create(name='host1')
	self.service1 = Service.objects.create(name='service1')
	self.service2 = Service.objects.create(name='service2')
        self.events = list()

        self.alert1 = Alert.objects.create(host=self.host,service=self.service1,status=Status.objects.get(pk=1),date=now(),info='Test alert WARNING')
        self.alert2 = Alert.objects.create(host=self.host,service=self.service1,status=Status.objects.get(pk=2),date=now()+timedelta(0,3),info='Test alert CRITICAL')
        self.alert3 = Alert.objects.create(host=self.host,service=self.service1,status=Status.objects.get(pk=5),date=now()+timedelta(0,6),info='Test alert OK')

        self.alert4 = Alert.objects.create(host=self.host,service=self.service2,status=Status.objects.get(pk=1),date=now(),info='Test alert WARNING')
        self.alert5 = Alert.objects.create(host=self.host,service=self.service2,status=Status.objects.get(pk=2),date=now()+timedelta(0,3),info='Test alert CRITICAL')
        self.alert6 = Alert.objects.create(host=self.host,service=self.service2,status=Status.objects.get(pk=5),date=now()+timedelta(0,3),info='Test alert OK')

    def tearDown(self):
	self.host.delete()
	self.service1.delete()
	self.service2.delete()
        [ A.delete() for A in Alert.objects.all() ]
        [ E.delete() for E in Event.objects.all() ]

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

def createAlert(host=None,service=None,status=None, isDown=True) :
    """
    Create a random alert from data in referentiel.
    Attributes may be choose with arguments.
    """
    if not host : host = choice(Host.objects.all())
    else : host = Host.objects.get(name=host)

    if not service : service = choice(Service.objects.all())
    else : service = Service.objects.get(name=service)

    if not status :
       if service.name == "Host status" :
           if isDown : status = Status.objects.get(name='DOWN')
           else : status = Status.objects.get(name='UP')
       else :
           if isDown : status = choice(Status.objects.exclude(Q(name='OK') | Q(name='UP') | Q(name='DOWN')))
           else : status = choice(Status.objects.exclude(Q(name='UP') | Q(name='DOWN')))
    else : status = Status.objects.get(name=status)

    A = Alert(
       host = host,
       service = service,
       status = status,
       date = now(),
       info = "TEST - Alerte #"+str(Alert.objects.count()),
    )
    return A
