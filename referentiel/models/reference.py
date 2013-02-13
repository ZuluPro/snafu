from django.db import models

class Reference_Manager(models.Manager):
	def web_filter(self, GET):
		qset = self.get_query_set()
		return list((
		  set(qset.filter(host__name__icontains=GET['q'])) |
		  set(qset.filter(service__name__icontains=GET['q']))
		))

class Reference(models.Model):
	"""
	SNAFU uses reference for know what to do with Alerts and Events.
	Without Reference Events can't create GLPI ticket or send mail.
	"""
	host = models.ForeignKey('Host', verbose_name=u'H\xf4te')
	service = models.ForeignKey('Service')
	status = models.ForeignKey('Status')

	escalation_contact = models.CharField(max_length=100, blank=True, null=True, verbose_name="Contact d'escalade")
	tendancy = models.CharField(max_length=200, blank=True, null=True, verbose_name='Tendance')
	outage = models.CharField(max_length=200, blank=True, null=True)
	explanation = models.CharField(max_length=200, blank=True, null=True, verbose_name='Explication')
	origin = models.CharField(max_length=100, blank=True, null=True, verbose_name='Origine')
	procedure = models.CharField(max_length=255, blank=True, null=True, verbose_name=u'Proc\xe9dure')

	mail_type = models.ForeignKey('MailType', verbose_name="Type d'incident")
	mail_group = models.ForeignKey('MailGroup', verbose_name=u'Groupe concern\xe9')
	mail_criticity = models.ForeignKey('MailCriticity', verbose_name=u'Criticit\xe9')

	glpi_urgency = models.ForeignKey('GlpiUrgency', blank=True, null=True, verbose_name='Urgence')
	glpi_priority = models.ForeignKey('GlpiPriority', blank=True, verbose_name=u'Priorit\xe9')
	glpi_impact = models.ForeignKey('GlpiImpact', verbose_name='Impact')
	glpi_category = models.ForeignKey('GlpiCategory', verbose_name=u'Cat\xe9gorie GLPI')
	glpi_source = models.CharField(max_length=128, blank=True, verbose_name='Source', help_text="Destinateur de l'alerte.")
	glpi_dst_group = models.ForeignKey('GlpiGroup', verbose_name=u"Groupe d'affectation")
	glpi_supplier = models.ForeignKey('GlpiSupplier', blank=True, null=True, verbose_name='Fournisseur')

	objects = Reference_Manager()
	class Meta:
		app_label = 'referentiel'
		ordering = ['host','service','status']

	def __unicode__(self):
		return self.host.name+' - '+self.service.name+' en '+self.status.name
