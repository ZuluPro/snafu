from django.conf import settings

from xmlrpclib import ServerProxy
from socket import SocketType,error,gaierror

class GLPI_manager(ServerProxy):

	def __init__(self, *args, **kwargs) :
		uri = settings.SNAFU['glpi-xmlrpc']
		ServerProxy.__init__(self, uri, *args, **kwargs)
		self.login()

	def login(self):
		"""
		Return loginInfo.
		"""
		try :
		   login_info = self.glpi.doLogin({
			 'login_name':settings.SNAFU['glpi-login'],
			 'login_password':settings.SNAFU['glpi-password']
		   })
		   self.session = login_info['session']

		except (error,gaierror), e: 
		   login_info = {'error':e}
		return login_info 

	def logout(self):
		"""Make logout."""
		self.glpi.doLogout()

	def is_on(self):
		"""
		Make a connection socket test.
		"""
		from urlparse import urlsplit

		S = SocketType()
		S.settimeout(2)
		errno = S.connect_ex((urlsplit(settings.SNAFU['glpi-url']).netloc, 80))
		S.close()

		if errno < 0 :
			return False
		return True 
		
	def create(self, **kwargs):
		"""
		Create objects from list of objects.
		"""
		data = {'session':self.session}
		data['fields'] = dict()
		for k,v in kwargs.items() :
			data['fields'][k] = v
		return self.glpi.createObjects(data)

	def list(self, itemtype) :
		"""List a type of object."""
		if itemtype == 'host' :
			result = list()
			for itemtype in ('computer','networkequipment') :
				result += self.glpi.listObjects({'session':self.session, 'itemtype':itemtype})
		else :
			data = {'session':self.session, 'itemtype':itemtype} 
			result = self.glpi.listObjects(data)
		return result

	def get(self, itemtype, glpi_id) :
		"""Get an object from its type and id."""
		if itemtype == 'host' :
			result = list()
			for itemtype in ('computer','networkequipment') :
				result += self.glpi.getObject({'session':self.session, 'itemtype':itemtype, 'id':glpi_id})
		else :
			data = {'session':self.session, 'itemtype':itemtype, 'id':glpi_id} 
			result = self.glpi.getObject(data)

		return result

	def delete(self, **kwargs) :
		"""
		Create objects from list of objects.
		"""
		data = {'session':self.session}
		data['fields'] = dict()
		for k,v in kwargs.items() :
			data['fields'][k] = dict( [ [o,False] for o in v ] )
		return self.glpi.deleteObjects(data)

	def create_ticket(self, data):
		"""Create a trouble ticket."""
		data['session'] = self.session
		return self.glpi.createTicket(data)

	def add_follow_up(self,ticket_id,content):
		"""Add te given content as follow-up to the givent ticket's id."""
		data = dict()
		data['ticket'] = ticket_id
		data['content'] = content
		data['session'] = self.session
		self.glpi.addTicketFollowup(data)

	def add_ticket_document(self,ticket_id,doc,name):
		"""
		Add te given content as follow-up to the givent ticket's id.
		"""
		data = dict()
		data['ticket'] = ticket_id
		data['base64'] = doc
		data['name'] = name
		data['session'] = self.session
		self.glpi.addTicketDocument(data)

	def get_ticket(self, ticket_id):
		"""Return attributes of a given ticket."""
		return self.glpi.getTicket({'session':self.session, 'ticket':ticket_id})
