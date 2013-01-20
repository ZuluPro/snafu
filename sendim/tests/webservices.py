"""
Test to use SNAFU webservices
"""

from django.utils import unittest
from django.test.client import Client

class Webservice_TestCase(unittest.TestCase):
    """
    Test to use webservice.
    """
    def setUp(self):
        self.client = Client()

    def test_index(self):
        """Test with client."""
        response = self.client.get('/snafu/webservice')
        self.assertEqual(response.status_code, 200)
        self.assertIn('This is an XML-RPC Service.',response.content)
