"""
Test to create alerts for service status (WARNING/CRITICAL/OK).
"""

from django.utils import unittest
from django.utils.timezone import now
from django.core import management

from referentiel.models import Host, Service, Status, Reference
from sendim.models import Alert, Event

from datetime import datetime, timedelta

class Basic_Alert_TestCase(unittest.TestCase):
    """
    Tests for a single WARNING alert.
    """
    def setUp(self):
        management.call_command('loaddata', 'test_host.json', database='default', verbosity=0)
        management.call_command('loaddata', 'test_supervisor.json', database='default', verbosity=0)

    def tearDown(self):
        Alert.objects.all().delete()

    def test_Alert_init_and_save(self):
        """
        Test to initialize alert with 'supervisor' arg and save it.
        Normally Supervisor will be add to the Host.
        """
        A = Alert(
          host = Host.objects.get(name='test host'),
          service = Service.objects.get(name='test service'),
          status = Status.objects.get(pk=1),
          info='test alert',
          date=now(),
          supervisor='Icinga Demo'
        )
        self.assertEqual(A.supervisor, 'Icinga Demo')

        A.save()
        H = Host.objects.get(name='test host')
        self.assertIsNotNone(H.supervisor)
        self.assertEqual(H.supervisor.name, 'Icinga Demo')

    def test_Alert_objects_create(self):
        """
        Test to create alert with 'supervisor'.
        Normally Supervisor will be add to the Host.
        """
        A = Alert.objects.create(
          host = Host.objects.get(name='test host'),
          service = Service.objects.get(name='test service'),
          status = Status.objects.get(pk=1),
          info='test alert',
          date=now(),
          supervisor='Icinga Demo'
        )
        H = Host.objects.get(name='test host')
        self.assertIsNotNone(H.supervisor)
        self.assertEqual(H.supervisor.name, 'Icinga Demo')
