from django.utils import unittest
from django.test.client import Client

from django.contrib.auth.models import User

class Login_TestCase(unittest.TestCase):

    def setUp(self):
	self.user = User.objects.create(username='user',password='password')

    def tearDown(self):
        self.user.delete()

    def test_index(self):
        client = Client()
        response = client.get('/snafu/login')
        self.assertEqual(response.status_code, 200)

    def test_good_login(self):
        client = Client()
        response = client.get('/snafu/login', {'username':'user','password':'password'})
        self.assertEqual(response.status_code, 200)

    def test_bad_login(self):
        client = Client()
        response = client.get('/snafu/login', {'username':'user','password':'pass'})
        self.assertEqual(response.status_code, 200)
