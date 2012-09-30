from django.shortcuts import render

from sendim.models import *
from referentiel.models import *

def eventHistory(request) :
    """Return a list of alerts which match with the primary alert of an event"""
    E = Event.objects.get( pk=request.GET['eventPk'])
    A = E.getPrimaryAlert()
    As = Alert.objects.filter(
       host__host=E.element.host,
       service__service=A.service.service
    )

    return render(request, 'eventHistory.html', {
        'As':As[::-1],
        'E':E
    } )


def eventReference(request) :
    E = Event.objects.get( pk=request.GET['eventPk'])
    A = E.getPrimaryAlert()
    R = A.reference

    return render(request, 'eventReference.html', {
        'R':R,
        'E':E,
        'A':A
    })

def eventAlerts(request) :
    E = Event.objects.get( pk=request.GET['eventPk'])
    return render(request, 'eventAlerts.html', {
        'E':E,
        'As':E.getAlerts()[::-1]
    })

def eventsFiltered(request) :
    events = Event.objects.all()
    if request.GET['pk'] : events = events.filter(pk=request.GET['pk'])
    if request.GET['element'] : events = events.filter(element__host__contains=request.GET['element'])
    if request.GET['glpi'] : events = events.filter(glpi__contains=request.GET['glpi'])
    if request.GET['message'] : events = events.filter(message__contains=request.GET['message'])
    if request.GET['date'] : pass 

    return render(request, 'events-li.html', { 'events':events[::-1] })
