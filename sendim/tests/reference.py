"""
"""

from django.utils import unittest
from django.utils.timezone import now
from django.core import management

from referentiel.models import Reference, Host, Service, Status
from sendim.models import Alert, Event

class Reference_TestCase(unittest.TestCase):
    """
    """
    def setUp(self):
        management.call_command('loaddata', 'test_host.json', database='default', verbosity=0)
        management.call_command('loaddata', 'test_reference.json', database='default', verbosity=0)
	self.host = Host.objects.get(pk=1)
	self.service = Service.objects.get(pk=2)
        self.alert = Alert.objects.create(host=self.host,service=self.service,status=Status.objects.get(pk=1),date=now(),info='Test alert')

    def tearDown(self):
        [ E.delete() for E in Event.objects.all() ]

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
