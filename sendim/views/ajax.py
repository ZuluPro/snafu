"""
Contains views which concern events and the modal.

Generaly in GET method, views return requested informations
or an error message which isn't an exception for show that in modal.

In POST method, it will return a redirect to '/snafu/events'.
"""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest

if 'djcelery' in settings.INSTALLED_APPS :
	from sendim import tasks
from sendim.models import *
from referentiel.models import *

@login_required
def reload_alerts(request) :
	"""Parse all active supervisors and put new alerts in database."""
	if Supervisor.objects.count() > 2 and not 'djcelery' in settings.INSTALLED_APPS :
		messages.add_message(request,messages.WARNING,u"<b>Trop de superviseurs !</b><br>Veuillez installer Django Celery ou pousser les alertes depuis le superviseur.")
	else :
		for S in Supervisor.objects.filter(active=True) :
			S_status = S.checkNagios()
			if not S_status :
				if 'djcelery' in settings.INSTALLED_APPS :
					result = tasks.reload_alerts.delay(S)
				else :
					S.parse()
				messages.add_message(request,messages.INFO,u'<b>Lecture de '+S.name+u" commenc\xe9e !</b>")
			else:
				messages.add_message(request, messages.ERROR,'<b>Erreur de lecture de '+S.name+' : '+str(S_status)+'</b>')
	return render(request, 'messages.html', {
		'messages':messages.get_messages(request),
	} )

@login_required
def eventHistory(request) :
	"""Return a list of alerts which match with the primary alert of an event."""
	E = Event.objects.get(pk=request.GET['eventPk'])
	A = E.get_primary_alert()
	As = A.get_similar()

	return render(request, 'modal/eventHistory.html', {
		'As':As,
		'E':E
	} )

@login_required
def eventReference(request) :
	"""Get reference of primary alert of a given event."""
	E = Event.objects.get(pk=request.GET['eventPk'])
	A = E.get_primary_alert()

	return render(request, 'modal/eventReference.html', {
		'E':E,
		'A':A
	})

@login_required
def eventAlerts(request) :
	"""Get alerts which are linked to a given event."""
	E = Event.objects.get( pk=request.GET['eventPk'])
	return render(request, 'modal/eventAlerts.html', {
		'E':E,
		'As':E.get_alerts()[::-1]
	})

@login_required
def eventsFiltered(request) :
	"""
	Get events filtered by pk, element, glpi ticket number or message.
	If no filter is given, return the last 100 events.
	"""
	Es = Event.objects.filter(closed=False)
	try :
		if request.GET.get('pk',False) : Es = Es.filter(pk=request.GET['pk'])
		if request.GET.get('glpi',False) : Es = Es.filter(glpi__contains=request.GET['glpi'])
	except ValueError, e :
		return HttpResponseBadRequest(u'Donn\xe9es demand\xe9es invalides !')
		 
	if request.GET.get('element',False) : Es = Es.filter(element__name__contains=request.GET['element'])
	if request.GET.get('message',False) : Es = Es.filter(message__contains=request.GET['message'])
	#if request.GET.get('service',False) : Es = Es.filter(message__contains=request.GET['message'])
	#if request.GET.get('date',False) : pass 

	return render(request, 'event/tr.html', { 'Es':Es.order_by('-date')[:100] })

@login_required
def choosePrimaryAlert(request) :
	"""
	Choose which alert will be primary.
	In GET : Return list of event's alerts.
	In POST : Set primary alert from POST['chosenAlert'].
	"""
	if request.method == 'GET' :
		if not request.GET.get('eventPk') :
			return HttpResponse(u"<center><h4>Veuillez choisir un \xe9v\xe9nement !<h4></center>")
		E = Event.objects.get(pk=request.GET['eventPk'])

	if request.method == 'POST' :
		E = Event.objects.get(pk=request.POST['eventPk'])
		A = Alert.objects.get(pk=request.POST['chosenAlert'])
		A.set_primary()

	return render(request, 'modal/choosePrimaryAlert.html', {
		'E':E,
		'As':E.get_alerts()[::-1]
	})

@login_required
def eventsAgr(request) :
	"""
	Aggregate several events in one.
	In GET : Return list of events with them alerts.
	In POST : Use aggregate() to make it into POST['choicedEvent'].
	"""
	if request.method == 'POST' :
#		if not request.POST['toAgr'] : 
#			return HttpResponse(u"<center><h4>Veuillez choisir plusieurs \xe9v\xe9nements !<h4></center>")
		E = Event.objects.get(pk=request.POST['choicedEvent'])
		E.aggregate(request.POST.getlist('toAgr'), request.POST['message'], glpi=E.glpi, mail=E.mail, criticity=E.criticity)
		messages.add_message(request,messages.SUCCESS,u"Aggr\xe9gation d'\xe9v\xe9nement avec succ\xe8s." )
		
		return redirect('/snafu/events')
	else :
		if len(request.GET.getlist('events[]') ) < 2 :
			return HttpResponse(u"<center><h4>Veuillez choisir plusieurs \xe9v\xe9nements !<h4></center>")
		return render(request, 'modal/events-agr.html', {
			'events': Event.objects.filter(pk__in=request.GET.getlist('events[]')),
			'alerts': Alert.objects.order_by('-date')
		})

@login_required
def closeEvents(request) :
	"""
	Close events.
	In GET : Return list of events given in GET['events[]'].
	In POST : Use Event.close() to make it on events' id given in POST['eventsPk'].
	"""
	if request.method == 'POST' :
		closedEs = list()
		notClosedEs = list()
		for E in ( Event.objects.get(pk=pk) for pk in request.POST.getlist('eventsPk') ) :
			E.close()
			if E.closed : closedEs.append(E)
			else : notClosedEs.append(E)

		if closedEs : messages.add_message(request,messages.INFO,u"Cl\xf4ture de:"+''.join(['<li>'+str(E)+'</li>' for E in closedEs ] ) )
		if notClosedEs : messages.add_message(request,messages.ERROR,u"Ev\xe9nement non cl\xf4tr\xe9:"+''.join(['<li>'+str(E)+'</li>' for E in notClosedEs ] ) )
		return redirect('/snafu/events')

	else :
		if not request.GET.get('events[]', False) :
			return HttpResponse(u"<center><h4>Veuillez choisir un ou plusieurs \xe9v\xe9nements !<h4></center>")
		return render(request, 'modal/close-event.html', {
			'Es': [ Event.objects.get(pk=pk) for pk in request.GET.getlist('events[]') ][::-1],
		})
   
@login_required
def followUp(request) :
	"""
	Add a follow up to an event's GLPI ticket.
	In GET : Return asked event with a textarea.
	"""
	if request.method == 'POST' :
		E = Event.objects.get(pk=request.POST['eventPk'])
		E.add_follow_up(request.POST['content'])
		return redirect('/snafu/events')

	else :
		if not request.GET.get('eventPk', False) :
			return HttpResponse(u"<center><h4>Veuillez choisir un \xe9v\xe9nement !<h4></center>")
		E = Event.objects.get(pk=request.GET['eventPk'])
		if not E.glpi : 
			return HttpResponse(u"<center><h4>L'\xe9v\xe9nement n'a pas de num\xe9ro de ticket GLPI !<h4></center>")

	return render(request, 'modal/glpi-followup.html', {
		  'E':E,
		  'followups':E.get_ticket()['followups']
		})
   
