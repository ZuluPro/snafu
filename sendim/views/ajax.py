from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect

from sendim.models import *
from sendim.defs import *
from referentiel.models import *

@login_required
def eventHistory(request) :
    """Return a list of alerts which match with the primary alert of an event."""
    E = Event.objects.get( pk=request.GET['eventPk'])
    A = E.getPrimaryAlert()
    As = Alert.objects.filter(
       host__host=E.element.host,
       service__service=A.service.service
    )

    return render(request, 'modal/eventHistory.html', {
        'As':As[::-1],
        'E':E
    } )

@login_required
def eventReference(request) :
    """Get reference of primary alert of a given event."""
    E = Event.objects.get( pk=request.GET['eventPk'])
    A = E.getPrimaryAlert()
    R = A.reference

    return render(request, 'modal/eventReference.html', {
        'R':R,
        'E':E,
        'A':A
    })

@login_required
def eventAlerts(request) :
    """Get alerts which are linked to a given event."""
    E = Event.objects.get( pk=request.GET['eventPk'])
    return render(request, 'modal/eventAlerts.html', {
        'E':E,
        'As':E.getAlerts()[::-1]
    })

@login_required
def eventsFiltered(request) :
    """Get events filtered by pk, element, glpi ticket number or message."""
    Es = Event.objects.all()
    if request.GET['pk'] : Es = Es.filter(pk=request.GET['pk'])
    if request.GET['element'] : Es = Es.filter(element__host__contains=request.GET['element'])
    if request.GET['glpi'] : Es = Es.filter(glpi__contains=request.GET['glpi'])
    if request.GET['message'] : Es = Es.filter(message__contains=request.GET['message'])
    if request.GET.get('date',None) : pass 

    return render(request, 'event/tr.html', { 'Es':Es.order_by('-date') })

@login_required
def choosePrimaryAlert(request) :
    """Choose which alert will be primary.
    In GET : Return list of event's alerts.
    In POST : Set primary alert from POST['choosenAlert'].
    """
    if request.method == 'GET' :
        E = Event.objects.get(pk=request.GET['eventPk'])

    if request.method == 'POST' :
        E = Event.objects.get(pk=request.POST['eventPk'])
        A = Alert.objects.get(pk=request.POST['choosenAlert'])
        A.setPrimary()

    return render(request, 'modal/choosePrimaryAlert.html', {
        'E':E,
        'As':E.getAlerts()[::-1]
    })

@login_required
def eventsAgr(request) :
    """Aggregate several events in one.
    In GET : Return list of events with them alerts.
    In POST : Use aggregate() to make it into POST['choicedEvent']."""
    if request.method == 'POST' :
        agregate(request.POST.getlist('toAgr'), request.POST['choicedEvent'], request.POST['message'] )
        return redirect('/snafu/events')

    return render(request, 'modal/events-agr.html', {
        'events': [ Event.objects.get(pk=pk) for pk in request.GET.getlist('events[]') ][::-1],
        'alerts': Alert.objects.order_by('-date')
    })

@login_required
def closeEvents(request) :
    """Close events
    In GET : Return list of events given in GET['events[]'].
    In POST : Use Event.close() to make it on events' id given in POST['eventsPk']."""
    if request.method == 'POST' :
        for E in [ Event.objects.get(pk=pk) for pk in request.POST.getlist('eventsPk') ] :
            E.close()
        return redirect('/snafu/events')

    return render(request, 'modal/close-event.html', {
        'Es': [ Event.objects.get(pk=pk) for pk in request.GET.getlist('events[]') ][::-1],
    })
   
@login_required
def followUp(request) :
    """Add a follow up to an event's GLPI ticket.
    In GET : Return asked event with a textarea."""
    if request.method == 'POST' :
        E = Event.objects.get(pk=request.POST['eventPk'])
        addFollowUp(E.glpi, request.POST['content'])
        return redirect('/snafu/events')

    elif request.method == 'GET' :
        E = Event.objects.get(pk=request.GET['eventPk'])

    return render(request, 'modal/glpi-followup.html', {
      'E':E
    })
   
