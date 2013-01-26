"""
"""
from django.utils import unittest
from django.test.client import Client
from django.core import management
from django.contrib.auth.models import User

from referentiel.models import Reference

class Views_Configuration_TestCase(unittest.TestCase):
    def setUp(self):
        # Create user and log it
        management.call_command('loaddata', 'test_host.json', database='default', verbosity=0)
        management.call_command('loaddata', 'test_reference.json', database='default', verbosity=0)
	self.user = User.objects.create_user(username='user',password='password')
        self.client = Client()
        self.client.login(username='user',password='password')

    def tearDown(self):
        self.client.logout()
        self.user.delete()
        Reference.objects.all().delete()

    def test_index(self):
        response = self.client.get('/snafu/configuration')
        self.assertEqual(response.status_code, 200)

    def test_reference_configuration(self):
        response = self.client.get('/snafu/configuration/form/reference/0')
        self.assertEqual(response.status_code, 200)
        self.assertIn('configuration/reference/refs/form.html', [ t.name for t in response.templates ])

        basic_ref_post = {
          'host':1,
          'mail_group':1,
          'mail_type':1,
          'glpi_category':1,
          'glpi_dst_group':1,
          'glpi_supplier':1,
          'glpi_source':'Supervision',
          'escalation_contact':'',
          'tendancy':'',
          'outage':'',
          'explanation':'',
          'origin':'',
          'procedure':'',
        }

        simple_ref_post = basic_ref_post.copy()
        simple_ref_post['form_type'] = 'simple'
        simple_ref_post['service'] = 2
        simple_ref_post['status'] = 1
        simple_ref_post['mail_criticity'] = 1
        simple_ref_post['glpi_impact'] = 1
        simple_ref_post['glpi_priority'] = 1
        simple_ref_post['glpi_urgency'] = 1
        response = self.client.post('/snafu/configuration/ref/add',simple_ref_post)
        self.assertEqual(response.status_code, 200)
        self.assertIn('configuration/reference/tabs.html', [ t.name for t in response.templates ])
        
        host_ref_post = basic_ref_post.copy()
        host_ref_post['form_type'] = 'host'
        host_ref_post['service'] = 1
        host_ref_post['status'] = 4
        host_ref_post['mail_criticity'] = 1
        host_ref_post['glpi_impact'] = 1
        host_ref_post['glpi_priority'] = 1
        host_ref_post['glpi_urgency'] = 1
        response = self.client.post('/snafu/configuration/ref/add',host_ref_post)
        self.assertEqual(response.status_code, 200)
        self.assertIn('configuration/reference/tabs.html', [ t.name for t in response.templates ])
        
        big_ref_post = basic_ref_post.copy()
        big_ref_post['form_type'] = 'big'
        big_ref_post['service'] = 1
        big_ref_post['warning_criticity'] = 1
        big_ref_post['warning_impact'] = 1
        big_ref_post['warning_priority'] = 1
        big_ref_post['warning_urgency'] = 1
        big_ref_post['critical_criticity'] = 1
        big_ref_post['critical_impact'] = 1
        big_ref_post['critical_priority'] = 1
        big_ref_post['critical_urgency'] = 1
        big_ref_post['unknown_criticity'] = 1
        big_ref_post['unknown_impact'] = 1
        big_ref_post['unknown_priority'] = 1
        big_ref_post['unknown_urgency'] = 1
        response = self.client.post('/snafu/configuration/ref/add',big_ref_post)
        self.assertEqual(response.status_code, 200)
        self.assertIn('configuration/reference/tabs.html', [ t.name for t in response.templates ])
        
        response = self.client.get('/snafu/configuration/list/reference/', {'q':''})
        self.assertEqual(response.status_code, 200)
        self.assertIn('configuration/reference/refs/ul.html', [ t.name for t in response.templates ])

        response = self.client.get('/snafu/configuration/get/reference/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('configuration/reference/refs/ref.html', [ t.name for t in response.templates ])

        response = self.client.get('/snafu/configuration/form/reference/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('configuration/reference/refs/form.html', [ t.name for t in response.templates ])

