"""
"""

from django.utils import unittest
from django.utils.timezone import now
from django.core import management

from referentiel.models import Host, Service, Status, Reference
from sendim.models import Alert, Event
from sendim.tests.defs import create_event, create_alert

from datetime import datetime, timedelta

class Event_TestCase(unittest.TestCase):
    """
    Tests for a single WARNING alert.
    """
    def setUp(self):
        management.call_command('loaddata', 'test_supervisor.json', database='default', verbosity=0)
        management.call_command('loaddata', 'test_host.json', database='default', verbosity=0)

        self.event1 = create_event(create_alert())
        self.event1.message = 'Aggregation Event#1'
        self.event1.glpi = 10
        self.event1.mail = True
        self.event1.criticity = 'Mineur'
        self.event1.save()
        
        self.event2 = create_event(create_alert())
        self.event2.message = 'Aggregation Event#2'
        self.event2.glpi = None
        self.event2.mail = False
        self.event2.criticity = '?'
        self.event2.save()

    def tearDown(self):
        self.event1.delete()
        self.event2.delete()
        Alert.objects.all().delete()
        Event.objects.all().delete()

#    def test_Event(self):
#        """
#        """
#        pass

    def test_aggregation_into_treated(self):
        """
        Aggregate two events. One of both is treated,
        so the event must hold his fields.
        """
        # Count alerts for test
        event1_alerts = list(self.event1.get_alerts())
        event2_alerts = list(self.event2.get_alerts())

        # Test if event hold his field
        self.event1 = self.event1.aggregate([self.event2.pk])
        self.assertEqual(self.event1.get_alerts().count(), len(event1_alerts+event2_alerts))
        self.assertEqual(self.event1.glpi, 10)
        self.assertEqual(self.event1.criticity, self.event1.criticity)
        self.assertTrue(self.event1.mail)

    def test_aggregation_into_not_treated(self):
        """
        Aggregate two events. One of both is treated,
        so the event must hold his fields.
        """
        # Count alerts for test
        event1_alerts = list(self.event1.get_alerts())
        event2_alerts = list(self.event2.get_alerts())

        # Test if event hold his field
        self.event2 = self.event2.aggregate([self.event1.pk])
        self.assertEqual(self.event2.get_alerts().count(), len(event1_alerts+event2_alerts))
        self.assertEqual(self.event2.glpi, 10)
        self.assertEqual(self.event2.criticity, self.event1.criticity)
        self.assertTrue(self.event2.mail)
