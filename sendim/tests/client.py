"""
"""
from django.utils import unittest
from django.test.utils import override_settings
from django.test.client import Client
from django.core import management
from django.conf import settings
from django.contrib.auth.models import User

from djcelery.models import TaskMeta

from sendim.models import Alert, Event
from referentiel.models import Supervisor, Reference

class Login_TestCase(unittest.TestCase):
    def setUp(self):
	self.user = User.objects.create_user(username='user',password='password')
        self.client = Client()

    def tearDown(self):
        self.client.logout()
        self.user.delete()

    def test_index(self):
        """
        Test an unauthorized page and after the LOGIN_URL.
        """
        response = self.client.get('/snafu')
        self.assertEqual(response.status_code, 301)
        #self.assertRedirects(response, '/snafu/login?next=/snafu/')
        response = self.client.get('/snafu/login')
        self.assertEqual(response.status_code, 200)

    def test_good_login(self):
        """
        Test to access to page as a user.
        """
        self.client.post('/snafu/login', {'username':'user','password':'password'})
        T = self.client.login(username='user',password='password')
        response = self.client.get('/snafu/events')
        self.assertEqual(response.status_code, 200)

    def test_bad_login(self):
        """
        Test if site is restricted to anonymous users.
        """
        self.client.post('/snafu/login', {'username':'user','password':'pass'})
        response = self.client.post('/snafu/events', {'username':'user','password':'pass'})
        self.assertIn(response.status_code, (301,302))

class Customer_Client_TestCase(unittest.TestCase):
    def setUp(self):
        management.call_command('loaddata', 'test_supervisor.json', database='default', verbosity=0)
        management.call_command('loaddata', 'test_host.json', database='default', verbosity=0)
        management.call_command('loaddata', 'test_reference.json', database='default', verbosity=0)
	self.user = User.objects.create_user(username='user',password='password')
        self.client = Client()
        self.client.post('/snafu/login', {'username':'user','password':'password'})
    
    def tearDown(self):
        self.client.logout()
        self.user.delete()
        [ A.delete() for A in Alert.objects.all() ]
        [ E.delete() for E in Event.objects.all() ]
        [ T.delete() for T in TaskMeta.objects.all() ]

    def test_reload_alerts(self):
        response = self.client.post('/snafu/event/reloadAlerts')
        
    def test_treatment_without_reference(self):
        self.client.post('/snafu/event/reloadAlerts')
        E = Event.objects.all()[0]
        A = E.getPrimaryAlert()
        self.assertNotEqual(E.message, '?')

        response = self.client.post('/snafu/events',{'eventPk':E.pk,'treatment_q':''})
        self.assertNotIn('event/add-reference.html', response.templates)
        
        ref_post = {
          'eventPk':E.pk,
          'host':E.element.pk,
          'service':A.service.pk,
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
        if A.service.name == 'Host status' :
            ref_post['form_type'] = 'host'
            ref_post['status'] = A.status.pk
            ref_post['mail_criticity'] = 1
            ref_post['glpi_impact'] = 1
            ref_post['glpi_priority'] = 1
            ref_post['glpi_urgency'] = 1
        else :
            ref_post['form_type'] = 'big'
            ref_post['warning_criticity'] = 1
            ref_post['warning_impact'] = 1
            ref_post['warning_priority'] = 1
            ref_post['warning_urgency'] = 1
            ref_post['critical_criticity'] = 1
            ref_post['critical_impact'] = 1
            ref_post['critical_priority'] = 1
            ref_post['critical_urgency'] = 1
            ref_post['unknown_criticity'] = 1
            ref_post['unknown_impact'] = 1
            ref_post['unknown_priority'] = 1
            ref_post['unknown_urgency'] = 1
        
        self.client.post('/snafu/event/addref',ref_post)
        self.assertIsNotNone(Alert.objects.get(pk=A.pk).reference)

        response = self.client.post('/snafu/events',{'eventPk':E.pk,'treatment_q':''})
        self.assertIsNotNone(Event.objects.get(pk=E.pk))
        self.assertIn('event/preview-mail.html', [ T.name for T in response.templates])

        mail_post = {
          'eventPk':E.pk,
          'sendmail_q':'',
          'to':response.context['msg']['to'],
          'cc':response.context['msg']['cc'],
          'ccm':response.context['msg'].get('ccm',''),
          'subject':response.context['msg']['subject'],
          'body':response.context['msg']['body'],
          'graphList':response.context['graphList'],
        }
        response = self.client.post('/snafu/events', mail_post)
        self.assertTrue(Event.objects.get(pk=E.pk).mail)
        self.assertIn('event/event-index.html', [ T.name for T in response.templates])
        
