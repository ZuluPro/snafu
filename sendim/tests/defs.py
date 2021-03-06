from django.utils.timezone import now
from django.db.models import Q

from referentiel.models import Host, Service, Status, Reference
from sendim.models import Alert, Event

from random import choice
from datetime import datetime, timedelta
from time import sleep

def create_alert(host=None,service=None,status=None, isDown=True, supervisor=''):
	"""
	Create a random alert from data in referentiel.
	Attributes may be choose with arguments.
	>>> from django.core import management
	>>> management.call_command('loaddata', 'test_host.json', database='default', verbosity=0)
	>>> A = create_alert(host='test host')
	>>> A.host.name
	u'test host'
	"""
	if not host : host = choice(Host.objects.all())
	else : host = Host.objects.get(name=host)

	if not service : service = choice(Service.objects.all())
	else : service = Service.objects.get(name=service)

	if not status :
	   if service.name == "Host status" :
		   if isDown : status = Status.objects.get(name='DOWN')
		   else : status = Status.objects.get(name='UP')
	   else :
		   if isDown : status = choice(Status.objects.exclude(Q(name='OK') | Q(name='UP') | Q(name='DOWN')))
		   else : status = choice(Status.objects.exclude(Q(name='UP') | Q(name='DOWN')))
	else :
		status = Status.objects.get(name=status)

	A = Alert(
	   host = host,
	   service = service,
	   status = status,
	   date = now(),
	   info = "TEST - Alerte #"+str(Alert.objects.count()),
	   supervisor='Icinga Demo',
	)
	return A

def create_alert_from(alert, service=None, status=None, delta=1, isDown=True):
	"""
	Create a random alert from previous one given in argument.
	Only status may be chosen.
	>>> from django.core import management
	>>> from sendim.tests.defs import create_alert
	>>> from sendim.models import Alert
	>>> management.call_command('loaddata', 'test_host.json', database='default', verbosity=0)
	>>> A = create_alert_from(create_alert(host='test host'))
	>>> A.host.name
	u'test host'
	>>> [ A.delete for A in Alert.objects.all() ]
	[]
	"""
	if service :
		service = Service.objects.get(name=service)
	else:
		service = alert.service

	if status :
		status = Status.objects.get(name=status)

	else :
		if alert.service.name == 'Host status' :
			if alert.status.name == 'DOWN' :
				status = Status.objects.get(name='UP')
			else :
				status = Status.objects.get(name='DOWN')
		else :
			if isDown :
				status = choice(Status.objects.exclude(pk__in=(4,5,6)))
			else :
				status = Status.objects.get(pk=5)

	A = Alert(
	   host = alert.host,
	   service = service,
	   status = status,
	   date = alert.date+timedelta(0,delta),
	   info = "TEST - Alerte #"+str(Alert.objects.count()),
	)
	return A
		
def create_event(A, number=5, endUp=True, message=None, criticity=None, glpi=None, mail=False):
	"""
	Create a event from an alert. Event will have number of alert given in argument (by default 5).
	It may be chosen if the last alert will be OK or not.
	>>> from sendim.tests.defs import create_alert
	>>> from django.core import management
	>>> management.call_command('loaddata', 'test_host.json', database='default', verbosity=0)
	>>> E = create_event(create_alert(),3)
	>>> E.get_alerts().count()
	3
	>>> useless = [ E.delete() for E in Event.objects.all() ]
	""" 
	A.save()
	A.link()
	for i in xrange(number):
		if i == xrange(number)[-2] and endUp :
			_A = create_alert_from(A, status='OK')
			_A.save()
			_A.link()
			break
		elif i <= xrange(number)[-2] :
			_A = create_alert_from(A)
			_A.save()
			_A.link()

	E = A.event
	E.message = message or E.message
	E.criticity = criticity or E.criticity
	E.glpi = glpi or E.glpi
	E.mail = mail or E.mail
	return E

def end_event(E,number=3):
	"""
	Add alerts to an event for close it.
	Number of alert to add before close can be given in arguments.
	>>> from sendim.tests.defs import create_alert, create_event
	>>> from django.core import management
	>>> management.call_command('loaddata', 'test_host.json', database='default', verbosity=0)
	>>> E = create_event(create_alert(),2,False)
	>>> E.get_alerts().count()
	2
	>>> E = end_event(E,2)
	>>> E.get_alerts().count()
	4
	>>> useless = [ E.delete() for E in Event.objects.all() ]
	"""
	A = E.get_primary_alert()
	for i in xrange(number):
		sleep(1)
		if i >= xrange(number)[-1] :
		  _A = create_alert_from(A, status=Status.objects.get(name='OK'))
		  _A.save()
		  _A.link()
		else :  
		  _A = create_alert_from(A)
		  _A.save()
		  _A.link()
	return E

def internet_is_on():
	"""
	Try to connect to ifconfig.me website.
	"""
	from urllib2 import urlopen, URLError
	try:
		response = urlopen('http://209.160.40.165/',timeout=3)
		return True
	except URLError as err: 
		return False
