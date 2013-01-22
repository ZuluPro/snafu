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
        self.alert = Alert.objects.create(
          host=Host.objects.get(pk=1),
          service=Service.objects.get(pk=1),
          status=Status.objects.get(pk=1),
          date=now(),
          info='Test alert'
        )
        self.event = self.alert.link()
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

        response = self.client.get('/snafu/event/history', {'eventPk':self.event.pk})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('As' in response.context)
        self.assertTrue('E' in response.context)

        response = self.client.get('/snafu/event/reference', {'eventPk':self.event.pk})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('E' in response.context)
        self.assertTrue('A' in response.context)

        response = self.client.get('/snafu/event/history', {'eventPk':self.event.pk})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('E' in response.context)
        self.assertTrue('As' in response.context)

        response = self.client.get('/snafu/event/filter',{'message':'test'})
        self.assertEqual(response.status_code, 200)

    def test_GET_and_POST(self):
        # Test Event aggregation
        response = self.client.get('/snafu/event/agr')
