from django.db import models
from django.db.models import Q
from django.utils.timezone import now

from referentiel.models import Host, Service, Status, Reference, Translation
from sendim.models import Event

class Alert_Manager(models.Manager):
	"""Custom manager for alerts which return an AlertQuerySet."""
	def get_query_set(self):
		"""Use AlertQuerySet by default."""
		return AlertQuerySet(self.model)

	def __getattr__(self, name, *args):
		if name.startswith("_"): 
			raise AttributeError
		return getattr(self.get_query_set(), name, *args) 

	def create(self, *args, **kwargs):
		"""
		Create Alert and return it.
		supervisor arguments allow to link host to it.
		"""
		from referentiel.models import Supervisor

		# Try to find supervisor arg and corresponding object by name
		if Supervisor.objects.filter(name=kwargs.get('supervisor','')).exists() :
			S = Supervisor.objects.get(name=kwargs['supervisor'])
			del kwargs['supervisor']
			if not Host.objects.get(pk=kwargs['host'].pk).supervisor :
				Host.objects.filter(pk=kwargs['host'].pk).update(supervisor=S)
		return super(Alert_Manager, self).create(*args, **kwargs)

	def reference_web_filter(self, GET):
		qset = self.get_query_set().filter(reference=None, status__pk__in=[1,2,3,4])
		return list((
			set(qset.filter(host__name__icontains=GET['q'])) |
			set(qset.filter(service__name__icontains=GET['q']))
		))

	def translation_web_filter(self, GET):
		return self.get_query_set().filter(translation=None, service__name=GET['q'], status__pk__in=[4,5,6])

class AlertQuerySet(models.query.QuerySet):
	"""Custom QuerySet with methods adapted for alerts."""
	def get_host_alert(self):
		"""Get only Host status alerts."""
		return self.filter(service__name='Host status')

	def get_service_alert(self):
		"""Get only service status alerts."""
		return self.exclude(service__name='Host status')

	def get_problem_alert(self):
		"""Get WARNING, CRITICAL, UNKNOWN or DOWN alerts."""
		return self.filter(status__pk__in=(1,2,3,4))

	def get_ok_alert(self):
		"""Get OK or UP alerts."""
		return self.filter(status__pk__in=(5,6))

	def get_without_reference(self):
		"""
		Get alerts which reference is None and status is
		WARNING, CRITICAL or UNKNOW.
		"""
		return self.get_problem_alert().get_service_alert().filter(reference=None)

	def get_by_date(self, date=lambda:now().date()):
		"""
		Get day's alerts by date. By default return for today.
		"""
		from datetime import datetime

		if isinstance(date, datetime) :
			date = date.date()
		return self.filter(date=date)

class Alert(models.Model) :
	host = models.ForeignKey('referentiel.Host')
	service = models.ForeignKey('referentiel.Service')
	status = models.ForeignKey('referentiel.Status')
	date = models.DateTimeField()
	info = models.CharField(max_length=300)
	event = models.ForeignKey('Event', blank=True, null=True)
	reference = models.ForeignKey('referentiel.Reference', blank=True, null=True, on_delete=models.SET_NULL)
	translation = models.ForeignKey('referentiel.Translation', blank=True, null=True, on_delete=models.SET_NULL)
	isPrimary = models.BooleanField(default=False)

	objects = Alert_Manager()
	class Meta:
		app_label = 'sendim'
		ordering = ('date',)

	def __init__(self, *args, **kwargs):
		# Reference temporaly Supervior in Alert object
		if 'supervisor' in kwargs :
			self.supervisor = kwargs['supervisor']
			del kwargs['supervisor']
		super(Alert,self).__init__(*args, **kwargs)

	def __unicode__(self) :
		return self.host.name+' : '+self.service.name+' - '+ self.status.name

	def save(self, *args, **kwargs):
		"""
		If Alert has attribute 'supervisor' and it exists,
		put it into Host attribute automaticaly.
		"""
		if 'supervisor' in dir(self) :
			from referentiel.models import Host, Supervisor
			# If Supervisor exists and attribute is not empty
			if Supervisor.objects.filter(name__icontains=self.supervisor) and self.supervisor :
				S = Supervisor.objects.filter(name__icontains=self.supervisor)[0]
				# If host doesn't have a supervisor
				if not Host.objects.get(pk=self.host.pk).supervisor :
					Host.objects.filter(pk=self.host.pk).update(supervisor=S)
		super(Alert, self).save(*args, **kwargs)

	def set_primary(self):
		"""Set alert as primary, set all event's alerts as not."""
		self.event.get_alerts().update(isPrimary=False)
		self.isPrimary = True
		self.save()

	def is_black_listed(self):
		"""
		Return True if this Alert corresponding to a Black_reference.
		"""
		from referentiel.models import Black_reference

		if Black_reference.objects.filter(host=self.host,service=self.service).exists() :
			return True
		else :
			return False

	def get_similar(self, host_status=True, exclude_self=False):
		"""Return alerts which have the same host and service."""
		if host_status :
			As = Alert.objects.filter(
			  Q(host=self.host),
			  Q(service=self.service) | Q(service__name='Host status')
			)
		else:
			As = Alert.objects.filter(host=self.host,service=self.service)
		# Exclude or not self
		if exclude_self :
			return As.exclude(pk=self.pk)
		else:
			return As

	def get_ReferenceForm(self):
		"""
		Get a ReferenceForm or an HostReferenceForm.
		"""
		from referentiel.forms import HostReferenceForm, ReferenceForm
		data = {
		  'glpi_source':'Supervision',
		  'host':self.host,
		  'service':self.service,
		  'status':self.status
		}
		if self.status.name == "DOWN" :
			data['form_type'] = 'host'
			form = HostReferenceForm
		else :
			data['form_type'] = 'simple'
			form = ReferenceForm
		return form(data=data)

	def get_TranslationForm(self):
		"""
		Get a TranslationForm.
		"""
		from referentiel.forms import TranslationForm
		data = {
		  'service':self.service,
		  'status':self.status
		}
		return TranslationForm(data=data)

	def find_reference(self, update=True, byHost=True, byService=True, byStatus=True):
		"""
		Return a Reference which matching with the Alert.
		Searching parameters may be given with arguments.
		""" 
		from referentiel.models import Reference

		if not self.reference :
			Rs = Reference.objects.all()
			if byHost : Rs = Rs.filter(host=self.host)
			if byService : Rs = Rs.filter(service=self.service)
			if byStatus : Rs = Rs.filter(status=self.status)
			if Rs and update : 
				R = Rs[0]
				self.reference = R
				self.save()
				return R
		else : return self.reference

	def find_translation(self, update=True, byStatus=True):
		"""
		Return a Translation which matching with the Alert.
		""" 
		if not self.translation :
			Ts = Translation.objects.all()
			if byStatus : Ts = Ts.filter(service=self.service, status=self.status)
			if Ts and update :
				T = Ts[0]
				self.translation = T
				self.save()
				return T
		else : return self.translation

	def link_to_reference(self, force=False, byHost=True, byService=True, byStatus=True):
		"""
		Search if a reference matches with the alert.
		In case, link alert to it.
		"""
		if ( self.reference and force ) or not self.reference : 
			self.reference = self.find_reference(byHost, byService, byStatus)
			if self.reference : self.save()
		return self.reference

	def link_to_translation(self, force=False, byStatus=True):
		"""
		Search if a translation matches with the alert.
		In case, link alert to it.
		"""
		if ( self.translation and force ) or not self.translation : 
			self.translation = self.find_translation(byStatus)
			self.save()
		return self.reference

	def link_to_event(self,event):
		"""
		Link alert to the given event.
		If service is 'Host status', it will become primary.
		"""
		self.event = event
		if self.status.name == 'DOWN' :
			self.set_primary()
		self.save()
		return self.event

	def create_event(self,message,mail_criticity='?'):
		"""
		Create an Event corresponding to Alert.
		"""
		E = Event.objects.create(
		  element = self.host,
		  date = self.date,
		  criticity = mail_criticity,
		  message = message
		)
		self.event = E
		self.set_primary()
		self.save()
		return E

	def link(self) :
		"""
		Used for link an alert to Event. Take all case for alerts :
		 - If alert is OK/UP : Link to event
		 - If previous similar alert is DOWN : Link to previous alert's event
		 - If previous similar alert is OK/UP : Create event and link
		 - If no previous similar alert : Create Event and link
		etc...
		"""
		if not self.event :
			# Return None if alert is OK and no corresponding alert is found
			if self.status.name in ('OK','UP') :
				if self.get_similar(exclude_self=True).exclude(event=None).exists() :
					E = self.get_similar(exclude_self=True).exclude(event=None).order_by('-date')[0].event
					self.event = E
					self.save()
				else :
					return None
			else :
				# Put reference or '?'
				if self.find_reference():
					mail_criticity = self.reference.mail_criticity
				else:
					mail_criticity = '?'

				# Put translation or Alert.info
				if self.find_translation():
					translation = self.translation.translation
				else:
					translation = self.info

				# If there's no similar alert, create Event
				if not self.get_similar(exclude_self=True).exclude(event=None).exists() :
					E = self.create_event(translation,mail_criticity)

				# Else find the last alert
				else :
					lastA = self.get_similar(exclude_self=True).exclude(event=None).order_by('-date')[0]
					# If last alert is OK/UP, then create an Event
					if lastA.status.name in ('OK','UP') :
						E = self.create_event(translation,mail_criticity)
					# Else link current alert to lastA.event
					else : 
						E = self.link_to_event(lastA.event)
			return E
		else :
			return self.event

	def get_downtime_status(self):
		"""Get Downtime for current Host and Service."""
		from sendim.models import Downtime
		D = Downtime.objects.get(host=self.host,service=self.service)
		return D
