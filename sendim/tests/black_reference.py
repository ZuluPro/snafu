"""
"""
from django.utils import unittest
from django.core import management

from sendim.tests.defs import *
from referentiel.models import Host, Service, Status, Black_reference, Reference
from sendim.models import Alert, Event

class Black_reference_TestCase(unittest.TestCase):
    """
    Tests for a single WARNING alert.
    """
    def setUp(self):
        management.call_command('loaddata', 'test_host.json', database='default', verbosity=0)
        self.alert = create_alert(service='test service')
        self.black_reference = Black_reference.objects.create(
          host=self.alert.host,
          service=self.alert.service
        )

    def tearDown(self):
        [ A.delete() for A in Alert.objects.all() ]
        [ E.delete() for E in Event.objects.all() ]

    def test_alert_link_to_event(self):
        """
        """
        self.assertTrue(self.alert.is_black_listed())
