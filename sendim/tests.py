from django.db.models import Q

from referentiel.models import Host, Service, Status, Reference
from referentiel.defs import getReference
from sendim.models import Alert, Event

from random import choice
from datetime import datetime
from time import sleep

def createAlert(host=None,service=None,status=None, isDown=True) :
    """Create a random alert from data in referentiel.
    Attributes may be choose with arguments."""
    if not host : host = choice(Host.objects.all())
    else : host = Host.objects.get(host=host)

    if not service : service = choice(Service.objects.all())
    else : service = Service.objects.get(service=service)

    if not status :
       if service.service == "Host status" :
           if isDown : status = Status.objects.get(status='DOWN')
           else : status = Status.objects.get(status='UP')
       else :
           if isDown : status = choice(Status.objects.exclude(Q(status='OK') | Q(status='UP') | Q(status='DOWN')))
           else : status = choice(Status.objects.exclude(Q(status='UP') | Q(status='DOWN')))
    else : status = Status.objects.get(status=status)

    A = Alert(
       host = host,
       service = service,
       status = status,
       date = datetime.now(),
       info = "TEST - Alerte #"+str(Alert.objects.count()),
    )
    return A

def createAlertFrom(alert, status=None, isDown=True):
    """Create a random alert from previous one given in argument.i
    Only status may be chosen."""
    if alert.service.service == 'Host status' :
        if alert.status == Status.objects.get(status='DOWN') : status = Status.objects.get(status='UP')
        else : status = Status.objects.get(status='DOWN')
    else :
        if status : Status.objects.get(status=status)
        else : 
            status = Status.objects.exclude(Q(status='DOWN') | Q(status='UP'))
            if isDown : status = choice(status.exclude(status='OK'))
            else : status = choice(status)

    A = Alert(
       host = alert.host,
       service = alert.service,
       status = status,
       date = datetime.now(),
       info = "TEST - Alerte #"+str(Alert.objects.count()),
    )
    A.save()
    return A
        
def createEvent(A, number=5, endUp=True):
    """Create a event from an alert. Event will have number of alert given in argument (by default 5).
    It may be chosen if the last alert will be OK or not""" 
    A.save()
    A.link()
    for i in xrange(number):
        sleep(1)
        if i == xrange(number)[-2] and endUp :
            _A = createAlertFrom(A, status=Status.objects.get(status='OK'))
            _A.save()
            _A.link()
            break
        elif i <= xrange(number)[-2] :
            _A = createAlertFrom(A)
            _A.save()
            _A.link()
    return A.event

def endEvent(E,number=3):
    """Add alerts to an event for close it.
    Number of alert to add before close can be given in arguments."""
    A = E.getPrimaryAlert()
    for i in xrange(number):
        sleep(1)
        if i >= xrange(number)[-1] :
          _A = createAlertFrom(A, status=Status.objects.get(status='OK'))
          _A.save()
          _A.link()
        else :  
          _A = createAlertFrom(A)
          _A.save()
          _A.link()
    return E
