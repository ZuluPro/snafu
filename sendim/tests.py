from django.db.models import Q

from referentiel.models import *
from referentiel.defs import getReference
from sendim.models import *

from random import choice
from datetime import datetime

def createAlert(host=None,service=None,status=None, isDown=True) :
    if not host : host = choice(Host.objects.all())
    else : host = Host.objects.get(host=host)

    if not service : service = choice(Service.objects.all())
    else : service = Service.objects.get(service=service)

    if not status :
       if service.service == "Host status" :
	   print 123
           if isDown : status = Status.objects.get(status='DOWN')
           else : status = Status.objects.get(status='UP')
       else :
           print 535
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

def createAlertFrom(alert, isDown=True):

    if alert.service.service == 'Host status' :
        print 123
        if alert.status == Status.objects.get(status='DOWN') : status = Status.objects.get(status='UP')
        else : status = Status.objects.get(status='DOWN')
    else :
        print 435
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
        


def getUnrefAlerts() :
    As = Alert.objects.filter(reference=None)
    return As
