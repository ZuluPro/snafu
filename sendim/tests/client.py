from django.utils import unittest
from django.test.client import Client

from django.contrib.auth.models import User

class Login_TestCase(unittest.TestCase):

    def setUp(self):
	self.user = User.objects.create_user(username='user',password='password')
        self.client = Client()

    def tearDown(self):
        self.client.logout()
        self.user.delete()

    def test_index(self):
        response = self.client.get('/snafu')
        self.assertEqual(response.status_code, 301)
        #self.assertRedirects(response, '/snafu/login?next=/snafu/')
        response = self.client.get('/snafu/login')
        self.assertEqual(response.status_code, 200)

    def test_good_login(self):
        self.client.post('/snafu/login', {'username':'user','password':'password'})
        T = self.client.login(username='user',password='password')
        response = self.client.get('/snafu/events')
        self.assertEqual(response.status_code, 200)

    def test_bad_login(self):
        self.client.post('/snafu/login', {'username':'user','password':'pass'})
        response = self.client.post('/snafu/events', {'username':'user','password':'pass'})
        self.assertIn(response.status_code, (301,302))
