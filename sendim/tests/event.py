"""
"""

from django.utils import unittest
from django.utils.timezone import now
from django.core import management

from referentiel.models import Host, Service, Status, Reference
from sendim.models import Alert, Event
from sendim.test.defs import create_event, create_alert

from datetime import datetime, timedelta

class Event_TestCase(unittest.TestCase):
    """
    Tests for a single WARNING alert.
    """
    def setUp(self):
        management.call_command('loaddata', 'test_supervisor.json', database='default', verbosity=0)
        management.call_command('loaddata', 'test_host.json', database='default', verbosity=0)

    def tearDown(self):
        Alert.objects.all().delete()
        Event.objects.all().delete()

    def test_Event(self):
        """
        """
        pass
