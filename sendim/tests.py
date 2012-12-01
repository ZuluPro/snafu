"""
Function for create alerts and events.
"""

from django.db.models import Q

from referentiel.models import Host, Service, Status, Reference
from sendim.models import Alert, Event

from random import choice
from datetime import datetime
from time import sleep

def createAlert(host=None,service=None,status=None, isDown=True) :
    """
    Create a random alert from data in referentiel.
    Attributes may be choose with arguments.
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
    else : status = Status.objects.get(name=status)

    A = Alert(
       host = host,
       service = service,
       status = status,
       date = datetime.now(),
       info = "TEST - Alerte #"+str(Alert.objects.count()),
    )
    return A

def createAlertFrom(alert, status=None, isDown=True):
    """
    Create a random alert from previous one given in argument.i
    Only status may be chosen.
    """
    if alert.service.name == 'Host status' :
        if alert.status == Status.objects.get(name='DOWN') : status = Status.objects.get(name='UP')
        else : status = Status.objects.get(name='DOWN')
    else :
        if status : Status.objects.get(name=status)
        else : 
            status = Status.objects.exclude(Q(name='DOWN') | Q(name='UP'))
            if isDown : status = choice(status.exclude(name='OK'))
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
    """
    Create a event from an alert. Event will have number of alert given in argument (by default 5).
    It may be chosen if the last alert will be OK or not.
    """ 
    A.save()
    A.link()
    for i in xrange(number):
        sleep(1)
        if i == xrange(number)[-2] and endUp :
            _A = createAlertFrom(A, status=Status.objects.get(name='OK'))
            _A.save()
            _A.link()
            break
        elif i <= xrange(number)[-2] :
            _A = createAlertFrom(A)
            _A.save()
            _A.link()
    return A.event

def endEvent(E,number=3):
    """
    Add alerts to an event for close it.
    Number of alert to add before close can be given in arguments.
    """
    A = E.getPrimaryAlert()
    for i in xrange(number):
        sleep(1)
        if i >= xrange(number)[-1] :
          _A = createAlertFrom(A, status=Status.objects.get(name='OK'))
          _A.save()
          _A.link()
        else :  
          _A = createAlertFrom(A)
          _A.save()
          _A.link()
    return E
