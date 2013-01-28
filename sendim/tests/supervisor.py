"""
Test to use a supervisor
"""

from django.utils import unittest
from django.core import management
from django.utils.timezone import now

from referentiel.models import Supervisor, Host, Service
from sendim.models import Alert, Event, Downtime

class Supervisor_TestCase(unittest.TestCase):
    """
    Test to use Supervisors.
    """
    def setUp(self):
        management.call_command('loaddata', 'test_supervisor.json', database='default', verbosity=0)
	self.supervisor = Supervisor.objects.get(pk=1)

    def tearDown(self):
        Alert.objects.all().delete()
        Event.objects.all().delete()
        Downtime.objects.all().delete()

    def test_communication(self):
        """Test a simple HTTP communication with Supervisor."""
        response = self.supervisor.checkNagios()
        self.assertFalse(response)

    def test_logged_in_communication(self):
        """Test to access to a page which need login."""
        opener = self.supervisor.getOpener()
        opener.open(self.supervisor.index)

    def test_parsing(self):
        """Test to parse a supervisor."""
        self.supervisor.parse()
        if Alert.objects.count() :
            A = Alert.objects.all()[0]
            self.assertNotEqual(Host.objects.count(), 0)
            self.assertNotEqual(Service.objects.count(), 0)
            self.assertEqual(self.supervisor.name, A.host.supervisor.name)

    def test_parsing_with_downtime(self):
        """
        Test to parse a supervisor.
        And re-test to parse with downtime
        """
        first_count = len(self.supervisor.parse())
        if Alert.objects.exists() :

            A = Alert.objects.exclude(service__name='Host status')[0]
            D = A.get_downtime_status()
            D.status = 'STARTED'
            D.save()

            Alert.objects.all().delete()
            Event.objects.all().delete()
            new_count = len(self.supervisor.parse())
            self.assertNotEqual(first_count,new_count)
