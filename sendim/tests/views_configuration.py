"""
"""
from django.utils import unittest
from django.test.client import Client
from django.core import management
from django.contrib.auth.models import User

from sendim.models import Alert, Event
from referentiel.models import Host, Service, Status

class Views_Configuration_TestCase(unittest.TestCase):
    def setUp(self):
        # Create user and log it
	self.user = User.objects.create_user(username='user',password='password')
        self.client = Client()
        self.client.login(username='user',password='password')

    def tearDown(self):
        self.client.logout()
        self.user.delete()
        [ A.delete() for A in Alert.objects.all() ] 
        [ E.delete() for E in Event.objects.all() ] 

    def test_index(self):
        """
        """
        response = self.client.get('/snafu/configuration')
        self.assertEqual(response.status_code, 200)

#    def test_configuration_manager(self):
#        MODELS = (
#         'host', 'user', 'reference', 'hostReference',
#         'a_reference', 'translation', 'a_translation',
#         'supervisor', 'glpiUser', 'glpiGroup', 'category',
#         'supplier', 'template', 'mailType', 'mailGroup',
#        )
#        ACTIONS = (
#         'list','form','del','get','add','update'
#        )
#        for model in MODELS :
#            actions = ('form','add','get','list','del')
#            for action in actions :
#                response = self.client.get('/snafu/configuration/'+action+'/'+'model')
#                self.assertEqual(response.status_code, 200)
