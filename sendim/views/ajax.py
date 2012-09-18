from django.shortcuts import render

from sendim.models import *
from referentiel.models import *

def eventHistory(request) :
    E = Event.objects.get( pk=request.GET['eventPk'])
    A = Alert.objects.filter(date__exact=E.date)[0]
    alerts = Alert.objects.filter(
       host__host__exact=E.element.host,
       service__service__exact=A.service.service
    )

    return render(request, 'eventHistory.html', {
        'alerts':alerts[::-1],
        'event':E
    } )


def eventReference(request) :
    E = Event.objects.get( pk=request.GET['eventPk'])
    A = Alert.objects.filter(event=E)[0]
    R = Reference.objects.filter(
        service__service__exact=A.service.service,
        status__status__exact=A.status.status
    )[0]

    return render(request, 'eventReference.html', {
        'reference':R,
        'event':E,
        'alert':A
    })

def eventAlerts(request) :
    E = Event.objects.get( pk=request.GET['eventPk'])
    A = Alert.objects.filter(event=E)

    return render(request, 'eventAlerts.html', {
        'event':E,
        'alerts':A[::-1]
    })

def eventsFiltered(request) :
    events = Event.objects.all()
    if request.GET['pk'] : events = events.filter(pk=request.GET['pk'])
    if request.GET['element'] : events = events.filter(element__host__contains=request.GET['element'])
    if request.GET['glpi'] : events = events.filter(glpi__contains=request.GET['glpi'])
    if request.GET['message'] : events = events.filter(message__contains=request.GET['message'])
    if request.GET['date'] : pass 

    return render(request, 'events-li.html', { 'events':events[::-1] })
