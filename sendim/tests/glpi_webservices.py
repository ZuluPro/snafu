"""
"""
from django.utils import unittest
from django.core import management

from sendim.defs import get_from_glpi, list_from_glpi
from sendim.connection import doLogin, doLogout, glpiServer

class GLPI_webservices(unittest.TestCase):
    def setUp(self):
        self.items = dict()
        self.ITEM_TYPES = (
          'host',
          'itilcategory',
          'user',
          'group',
        )

    def tearDown(self):
        del self.items

    def test_checkGLPI(self):
        response = doLogin()
        self.assertNotIn('error', response)

    def test_list_from_glpi(self):
        for item_type in self.ITEM_TYPES :
            self.items[item_type] = list_from_glpi(item_type)
