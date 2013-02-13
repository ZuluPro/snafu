from django.db import models

class MailType_Manager(models.Manager):
	def web_filter(self, GET):
		return self.get_query_set().filter(name__icontains=GET['q'])

class MailType(models.Model):
	name = models.CharField(max_length=50, unique=True, verbose_name='Nom')

	objects = MailType_Manager()
	class Meta:
		app_label = 'referentiel'

	def __unicode__(self):
		return self.name

class MailGroup_Manager(models.Manager):
	def web_filter(self, GET):
		qset = self.get_query_set()
		return list((
		  set(qset.filter(to__icontains=GET['q'])) |
		  set(qset.filter(ccm__icontains=GET['q'])) |
		  set(qset.filter(cc__icontains=GET['q']))
		))

class MailGroup(models.Model):
	name = models.CharField(max_length=30, unique=True, verbose_name='Nom')
	to = models.CharField(max_length=150, verbose_name=u'\xc0')
	cc = models.CharField(max_length=150, verbose_name='cc')
	ccm = models.CharField(max_length=150, verbose_name='cc majeur', help_text=u"Envoyer \xe0 ce contact en cas d'incident majeur")

	objects = MailGroup_Manager()
	class Meta:
		app_label = 'referentiel'

	def __unicode__(self):
		return self.name

class MailCriticity(models.Model):
	name = models.CharField(max_length=20, unique=True, verbose_name='Nom')

	class Meta:
		app_label = 'referentiel'

	def __unicode__(self):
		return self.name


