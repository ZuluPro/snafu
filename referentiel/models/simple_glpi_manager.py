from django.db.models import Manager

class SimpleGLPI_Manager(Manager):
	def __init__(self, *args, **kwargs):
		self.type = kwargs['type']
		del kwargs['type']
		super(SimpleGLPI_Manager, self).__init__(*args, **kwargs)

	def web_filter(self, GET):
		return self.get_query_set().filter(name__icontains=GET['q'])

	def glpi_list(self):
		"""List objects from GLPI."""
		from sendim.glpi_manager import GLPI_Manager
		GLPI_Manager = GLPI_Manager()
		return GLPI_Manager.list(self.type)

	def glpi_get(self, glpi_id):
		"""Get object from GLPI."""
		from sendim.glpi_manager import GLPI_Manager
		GLPI_Manager = GLPI_Manager()
		return GLPI_Manager.get(self.type, glpi_id)
