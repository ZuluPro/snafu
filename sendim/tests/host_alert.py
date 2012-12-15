from django.utils import unittest
from django.utils.timezone import now

from referentiel.models import Host, Service, Status, Reference
from sendim.models import Alert, Event

class SingleHost_SingleAlert_TestCase(unittest.TestCase):
    def setUp(self):
	self.host = Host.objects.create(name='host1')
        self.alert = Alert.objects.create(
          host=self.host,
          service=Service.objects.get(pk=1),
          status=Status.objects.get(pk=4),
          date=now(),info='Test alert'
        )

    def tearDown(self):
	self.host.delete()
        self.alert.delete()

    def test_alert_link_to_event(self):
        self.assertIsInstance(self.alert.link(), Event)

    def test_create_glpi_ticket(self):
        self.event = self.alert.link()
        ticket_id = self.event.create_ticket()
        self.assertIsInstance(int(ticket_id), int)

    def test_close_event(self):
        self.event = self.alert.link()
        self.event.close()
        self.assertFalse(self.event.closed)


class SingleHost_MultipleAlert_TestCase(unittest.TestCase):
    def setUp(self):
	self.host = Host.objects.create(name='host1')
        self.alert1 = Alert.objects.create(
          host=self.host,
          service=Service.objects.get(pk=1),
          status=Status.objects.get(pk=4),
          date=now(),info='Test alert'
        )
        self.alert2 = Alert.objects.create(
          host=self.host,
          service=Service.objects.get(pk=1),
          status=Status.objects.get(pk=6),
          date=now(),info='Test alert'
        )
        self.events = list()

    def tearDown(self):
	self.host.delete()
        self.alert1.delete()
        self.alert2.delete()
        [ E.delete() for E in self.events ]

    def test_alert_link_to_event(self):
        for A in Alert.objects.filter(event=None) :
            E = A.link()
            if not E in self.events : self.events.append(E)
        for E in self.events :
            self.assertIsInstance(E, Event)
        self.assertEqual(Event.objects.count(),1)

    def test_create_glpi_ticket(self):
        for A in Alert.objects.filter(event=None) :
            E = A.link()
            if not E in self.events : self.events.append(E)

        for E in self.events :
            ticket_id = E.create_ticket()
            self.assertIsInstance(int(ticket_id), int)

    def test_close_event(self):
        for A in Alert.objects.filter(event=None) :
            E = A.link()
            if not E in self.events : self.events.append(E)
        self.events[0].close()
        self.assertTrue(self.events[0].closed)
