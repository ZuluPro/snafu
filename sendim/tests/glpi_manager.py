"""
"""

from django.utils import unittest
from django.core import management
from django.conf import settings

from sendim.glpi_manager import GLPI_Manager
from sendim.tests.defs import create_event, create_alert

class GLPI_Manager_TestCase(unittest.TestCase):
	"""
	"""
	def setUp(self):
		management.call_command('loaddata', 'test_host.json', database='default', verbosity=0)
		management.call_command('loaddata', 'test_reference.json', database='default', verbosity=0)
		self.manager = GLPI_Manager()

	def test_objects_management(self):
		"""
		Tests to manage computers, do cris
		eation, listing, get and delete.
		"""
		glpi_status = self.manager.is_on()

		# Create a computer and try to find in list of them
		computer = self.manager.create(computer=[{'name':'Test'}])['computer'][0]
		computers = self.manager.list('computer')
		self.assertIn((computer['id'],computer['name']), [ (c['id'],c.get('name','')) for c in computers ])

		# Try to get it
		self.assertEqual(computer, self.manager.get('computer', computer['id']))

		# Try to delete it and don't find it in list
		self.manager.delete(computer=[computer['id']])
		computers = self.manager.list('computer')
		self.assertNotIn((computer['id'],computer['name']), [ (c['id'],c.get('name','')) for c in computers ])
		
	def test_ticket_management(self):
		from os.path import join
		from base64 import b64encode

		E = create_event(create_alert())
		E.create_ticket()

		# Try to add a picture to a document
		b64doc = b64encode(open(join(settings.BASEDIR, '../sendim/tests/python.png'), 'r').read())
		doc = b64doc
		self.manager.add_ticket_document(E.glpi, doc, 'python.png')

		# Try to add a follow-up
		self.manager.add_follow_up(E.glpi, 'Test follow-up')

		# Try to get the ticket and find added info
		ticket = self.manager.get_ticket(E.glpi)
		self.assertEqual(ticket['documents'][0]['filename'], 'python.png')
		self.assertEqual(ticket['followups'][0]['content'], 'Test follow-up')
