from django.db import models

from sendim.exceptions import UnableToConnectGLPI
from sendim.glpi_manager import GLPI_manager
GLPI_manager = GLPI_manager()

class Event(models.Model) :
	element = models.ForeignKey('referentiel.Host')
	date = models.DateTimeField()
	criticity = models.CharField(max_length=30)
	message = models.CharField(max_length=300)
	glpi = models.IntegerField(blank=True, null=True)
	mail = models.BooleanField(default=False)
	closed = models.BooleanField(default=False)

	def __init__(self, *args, **kwargs):
		super(Event, self).__init__(*args, **kwargs)

	class Meta:
		app_label = 'sendim'

	def __unicode__(self) :
		return str(self.pk)+':'+self.element.name+' - '+self.message

	def get_alerts(self, isUp=True, withoutRef=False):
		"""
		Return a QuerySet of event's alerts.
		It is possible to filter with 2 arguments :
		 - isUp : If False excludes UP/OK alerts.
		 - withoutRef = If True excludes alerts without reference.
		"""
		from sendim.models import Alert

		As = Alert.objects.filter(event=self).order_by('-date')
   		if not isUp :
			As = As.exclude(status__pk__in=(5,6))
		if withoutRef :
			As = As.filter(reference=None)
		return As

	def get_last_alert(self, isUp=False):
		"""Get the last alert of an event."""
		from sendim.models import Alert

		As = Alert.objects.filter(event=self).order_by('-date')
		if not isUp :
			As = As.exclude(status__pk__in=(5,6))
		return As[0]

	def get_primary_alert(self):
		"""
		Return primary alert of event.
		if there's no primary alert, set the first as primary.
		"""
		from sendim.models import Alert
		try : return Alert.objects.filter(event=self).get(isPrimary=True)
		except Alert.DoesNotExist :
			if self.get_alerts() :
				A = self.get_alerts()[0]
				#logprint("Event #"+str(self.pk)+" had no primary alert, set to the first Alert #"+str(A.pk), 'red')
				A.set_primary()
				return A
			else :
				try : self.delete()
				except AssertionError : pass
				return None
				#logprint("Event #"+str(self.pk)+" had no alert, it has been deleted", 'red')
		except Alert.MultipleObjectsReturned :
			A = self.get_alerts().filter(isPrimary=True)[0]
			A.set_primary()
			return A
			
	def get_reference(self):
		"""Return reference of primary alert."""
		return self.get_primary_alert().reference

	def create_ticket(self):
		 """
		 Create a GLPI ticket and add ticket number to self.glpi.
		 """
		 R = self.get_reference()
	 
		 # Creation du 1er contenu du ticket
		 content = "Descriptif : "+ self.message +"\nImpact :\nDate et heure : " +str(self.date)+ u"\nV\xe9rification : "
	 
		 item = self.element.glpi_id
		 if item is None : item = 0

		 if not R :
			 category = 1
			 recipient = source = 0
			 urgency = impact = 3
		 else :
			 category = R.glpi_category.glpi_id
			 recipient = R.glpi_dst_group.glpi_id
			 source = R.glpi_source
			 urgency = R.glpi_urgency.glpi_id
			 impact = R.glpi_impact.glpi_id

		 ticket = {
			 'type':1,
			 'category': category,
			 'title': self.element.name+' '+self.message,
			 'content':content,
			 'recipient': recipient,
			 'group':9,
			 'source': source,
			 #'itemtype' : self.element.host_type,
			 #'item' : item,
			 'urgency':urgency,
			 'impact':impact,
		 }
		 ticket_info = GLPI_manager.create_ticket(ticket)
		 #logprint( "Ticket #"+str(ticketInfo['id'])+" created", 'green' )
	 
		 # Sauvegarde dans BDD
		 self.glpi = ticket_info['id']
		 self.save()
		 #logprint( "Ticket #"+str(ticketInfo['id'])+" associate to Event #"+str(self.pk), 'green')
	 
		 return ticket_info['id']

	def add_follow_up(self,content):
		 """
		 Add a content to the event's ticket.
		 """
		 if self.glpi :
			  GLPI_manager.add_follow_up(self.glpi,content)

	def get_ticket(self):
		"""Return a dictionnary with GLPI ticket's attributes."""
		if self.glpi :
			ticket_info = GLPI_manager.get_ticket(ticket_id=self.glpi)
		else :
			ticket_info = dict()
		return ticket_info

	def close(self, force=False):
		"""
		Calculate if the event may be closed.
		If yes :  Close event
		If no : Do nothing, or close if force=True in arguments.
		"""
		
		if self.closed : return False
		else :
			hosts = {}
			for A in self.get_alerts() :
				if not A.host.name in hosts : hosts[A.host.name] = []
				if not A.service.name in hosts[A.host.name] : hosts[A.host.name].append(A.service.name)
			### Calcul de tout les service
			notOK = list()
			for host in hosts.keys() : 
				for service in hosts[host] :
					if service == 'Host status' :
						if not self.get_alerts().filter(host__name=host,service__name=service,status__pk=6) :
							notOK.append( (host,service) )
					else :
						if not self.get_alerts().filter(host__name=host,service__name=service,status__pk=5) :
							notOK.append( (host,service) )
			if not notOK :
				self.closed = True
				self.save()
		return self.closed 

	def make_mail(self):
		"""
		Using Event and the chosen MailTemplate for create
		a dictionnary which contains all mail attributes.
		"""
		from django.conf import settings
		from sendim.models import MailTemplate

		R = self.get_primary_alert().reference
		if MailTemplate.objects.filter(chosen=True).exists() :
			MT = MailTemplate.objects.get(chosen=True)
		else :
			MT = MailTemplate.objects.get(pk=1)
	
		msg = {}
		msg['from'] = settings.SNAFU['smtp-from']
		msg['to'] = R.mail_group.to
		if self.criticity == 'Majeur' : msg['to'] += ', '+ R.mail_group.ccm
		msg['cc'] = ' ,'.join( [  settings.SNAFU['smtp-from'], R.mail_group.cc] )
		msg['subject'] = MT.subject
		msg['body'] = MT.body
	
		return msg

	def prepare_mail(self,POST):
		"""
		Use request.POST from 'sendim/templates/event/preview-mail.html',
		for send an email.
		This function make all substitutions and return a Mail object.
		"""
		from django.conf import settings
		from email.mime.text import MIMEText
		from email.mime.multipart import MIMEMultipart
		
		A = self.get_primary_alert()
		# Recherche du MailGroup correspondant
		R = A.reference
	
		msg = MIMEMultipart()
		msg['From'] = settings.SNAFU['smtp-from']
		msg['To'] = POST['to']
		msg['Cc'] = POST['cc']
		if POST['ccm'] : msg['To'] += ', '+ R.mail_group.ccm
		subject = POST['subject']
		body = POST['body']
	
		# Make substitutions
		SUBS = (
			("$HOST$", A.host.name),
			("$MESSAGE$", self.message),
			("$MAIL_TYPE$", R.mail_type.name),
			("$CRITICITY$", self.criticity),
			("$GLPI$" , str(self.glpi)),
			("$GLPI-URL$", settings.SNAFU['glpi-url']+'front/ticket.form.php?id='),
			("$TRANSLATION", self.message),
			("$DATETIME$", self.date.strftime('%d/%m/%y - %H:%M:%S')),
			("$DATE$", self.date.strftime('%d/%m/%y')),
			("$TIME$", self.date.strftime('%H:%M:%S')),
			("$LOG$" , '\n'.join( [ A.date.strftime('%d/%m/%y %H:%M:%S - ')+A.service.name+' en ' +A.status.name+' - '+A.info for A in self.get_alerts() ] ) )
		) 
		for pattern,string in SUBS :
			body = body.replace(pattern, string)
			subject = subject.replace(pattern, string)
		# Add modified subject
		msg['Subject'] = msg.preamble = subject
		# Add modified body
		msg.attach(MIMEText(body.encode('utf8'), 'plain'))
		
		# Add graph to mail
		if 'graphList' in POST :
			graph_url_list = POST.getlist('graphList')
			for i in range(len(graph_url_list)):
				img = A.host.supervisor.get_graph(A, graph_url_list[i])
				msg.attach(img)

		return msg

	def send_mail(self,msg):
		"""
		Send given email objects with SNAFU settings.
		"""
		from django.conf import settings
		from smtplib import SMTP

		smtpObj = SMTP(settings.SNAFU['smtp-server'] , settings.SNAFU['smtp-port'] )
		# Use TLS if password is settled
		if 'smtp-password' in settings.SNAFU.keys() :
			smtpObj.ehlo()
			smtpObj.starttls()
			smtpObj.ehlo()
			smtpObj.login(settings.SNAFU['smtp-from'], settings.SNAFU['smtp-password'])
		smtpObj.sendmail( msg['From'] , msg['To'], msg.as_string() )
		smtpObj.close()
	
		self.mail=True
		self.save()

		self.add_mail_to_ticket(msg)
	
		return True

	def add_mail_to_ticket(self,msg):
		 """
		 Add the given mail object as follow up.
		 """
		 self.add_follow_up(msg.as_string())

	def aggregate(self, eventsPk, message='', glpi=None, mail=False, criticity='?') :
		"""
		Aggregate several events into this one.
		"""
		if len(eventsPk) < 1 :
			return None

		# Walk on events and hold in memory ticket,mail and criticity
		Es = Event.objects.filter(pk__in=eventsPk).exclude(pk=self.pk)
		for E in Es :
			if E.glpi and not self.glpi :
				glpi = E.glpi
			if E.mail and not self.mail :
				mail = True
			if E.criticity in ('Mineur','Majeur') and not self.criticity in ('Mineur','Majeur') :
				if E.criticity == 'Majeur' : 
					criticity = 'Majeur' 
				else :
					criticity = 'Mineur' 

			E.get_alerts().update(isPrimary=False,event=self)
			E.delete()

		# Apply message, ticket,mail and criticity
		self.message = message or self.message
		self.glpi = glpi or self.glpi
		self.mail = mail or self.mail
		self.criticity = criticity
		self.save()
		return self

	def get_ReferenceFormSet(self):
		"""
		Return a reference forms list.
		Used for ask References of Event's Alerts.
		"""
		from referentiel.models import Host, Service, Reference
		from referentiel.forms import HostReferenceForm, ReferenceBigForm
		from sendim.models import Alert

		service_alerts = dict()
		host_alerts = list()

		# Sort missing references in a dict
		for A in self.get_alerts() :
			if A.service.name != 'Host status' :
				# Create list of service if it doesn't exists
				if not A.host.name in service_alerts :
					service_alerts[A.host.name] = []
	
				if not A.service.name in service_alerts[A.host.name] and (not Reference.objects.filter(host=A.host,service=A.service).exists()) :
					service_alerts[A.host.name].append(A.service.name)
			else :
				if (not A.host.name in host_alerts) and (not Reference.objects.filter(host=A.host,service=1).exists()) :
					host_alerts.append(A.host.name)
	
		# Create a From for each
		form_list = list()
		## Treat service alerts
		for host,services in service_alerts.items() :
			for service in services :
				data = dict()
				data['host'] = Host.objects.get(name=host)
				data['service'] = Service.objects.get(name=service)
				data['glpi_source'] = 'Supervision'
				data['form_type'] = 'big'
				for status in ('warning','critical','unknown') :
					data[status+'_criticity'] = 1
					data[status+'_urgency'] = 3
					data[status+'_priority'] = 3
					data[status+'_impact'] = 3
				form_list.append(ReferenceBigForm(data))
		## Treat host alerts
		for host in host_alerts :
			data = dict()
			data['host'] = Host.objects.get(name=host)
			data['service'] = 1
			data['status'] = 4
			data['glpi_source'] = 'Supervision'
			form_list.append(HostReferenceForm(data))
			data['form_type'] = 'host'
	
		return form_list
	
