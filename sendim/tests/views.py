"""
"""
from django.utils import unittest
from django.utils.timezone import now
from django.test.client import Client
from django.core import management
from django.contrib.auth.models import User

from sendim.tests.defs import *
from sendim.models import Alert, Event
from referentiel.models import Host, Service, Status

class Views_TestCase(unittest.TestCase):
    def setUp(self):
        management.call_command('loaddata', 'test_host.json', database='default', verbosity=0)
        # Create a first alert with event
        self.alert1 = create_alert(service='test service')
        self.alert1.save()
        self.event1 = self.alert1.link()
        # Create a first alert with event
        self.alert2 = create_alert(service='test service')
        self.alert2.save()
        self.event2 = self.alert2.link()
        # Create user and log it
	self.user = User.objects.create_user(username='user',password='password')
        self.client = Client()
        self.client.login(username='user',password='password')

    def tearDown(self):
        self.client.logout()
        self.user.delete()
        [ A.delete for A in Alert.objects.all() ] 
        [ E.delete for E in Event.objects.all() ] 

    def test_simple_GET(self):
        """
        General tests for simple views in GET.
        """
        response = self.client.get('/snafu/events')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Es' in response.context)

        response = self.client.get('/snafu/apropos')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('license' in response.context)

        response = self.client.get('/snafu/event/history', {'eventPk':self.event1.pk})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('As' in response.context)
        self.assertTrue('E' in response.context)

        response = self.client.get('/snafu/event/reference', {'eventPk':self.event1.pk})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('E' in response.context)
        self.assertTrue('A' in response.context)

        response = self.client.get('/snafu/event/history', {'eventPk':self.event1.pk})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('E' in response.context)
        self.assertTrue('As' in response.context)

        response = self.client.get('/snafu/event/filter',{'message':'test'})
        self.assertEqual(response.status_code, 200)

    def test_event_aggregation(self):
        """
        """
        # Test GET request to get aggregation modal
        agr_get = {'events[]':[self.event1.pk,self.event2.pk]}
        response = self.client.get('/snafu/event/agr', agr_get)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('events' in response.context)
        self.assertTrue('alerts' in response.context)

        # Test POST requestion to aggregate events
        agr_post = {
          'toAgr':[self.event1.pk,self.event2.pk],
          'choicedEvent':self.event1.pk,
          'message':'test aggregated event'
        }
        response = self.client.post('/snafu/event/agr', agr_post)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.get(pk=self.event1.pk).message, 'test aggregated event')
