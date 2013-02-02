from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib import messages
import django.utils.simplejson as json

from sendim.defs import *
from sendim.models import Alert,Event
from sendim.forms import *
from sendim.exceptions import UnableToConnectGLPI
from referentiel.models import *
from referentiel.forms import *

@login_required
def events(request) :
    """
    List events and do processing on them.
    
    Processes are in POST method :
     - reloadAlert_q : Parse Nagios alert history page.
     - sendmail_q : Send a mail for a given event.
     - treatment_q : Make exploitation processes.
    """
    if request.method == 'POST' :

        if 'eventPk' in request.POST :
            eventPk = request.POST["eventPk"]
            E = Event.objects.get(pk=eventPk)
            A = E.get_primary_alert()

        if "sendmail_q" in request.POST :
            msg = E.prepare_mail(request.POST)
            if E.send_mail(msg) :
                messages.add_message(request,messages.SUCCESS,u"Envoi d'un mail pour l'\xe9v\xe9nement #"+str(E.pk)+"." )
            else :
                messages.add_message(request,messages.ERROR,u"Echec de l'nvoi d'un mail pour l'\xe9v\xe9nement #"+str(E.pk)+"." )

        elif "treatment_q" in request.POST :
	    if E.criticity == '?' or not E.get_primary_alert().reference : 
		
		Forms = getFormSet(E)
		return render(request, 'event/add-reference.html', {
			'Forms':Forms, 'E':E,
        		'title':'Snafu - Ajout de Reference'
		} )

            # If havn't create a GLPI ticket
            if not E.glpi :
               try :
                   E.create_ticket()
                   messages.add_message(request,messages.SUCCESS,"Ticket #"+str(E.glpi)+u" associ\xe9 \xe0 Event #"+str(E.pk))
               except UnableToConnectGLPI :
                   messages.add_message(request,messages.ERROR,u"Impossible de se connecter \xe0 GLPI.")
                   return redirect('/snafu/events')

            # Create a mail preview 
            msg = E.make_mail()

            # Retrieve graphs for the current Event
            graphList = readGraphs(E.element.name, A.service.name)
   
            return render(request,'event/preview-mail.html', {
                    'msg':msg,
                    'E':E,
                    'graphList':graphList,
                    'title':'Snafu - Envoi de mail'
            })
        Es = Event.objects.filter(closed=False).order_by('-date')
    else :
        [ E.delete() for E in Event.objects.all() if not E.get_alerts().exists() ]
        Es = Event.objects.filter(closed=False).order_by('-date')

        paginator = Paginator(Es, 100)
        page = request.GET.get('page')
        try:
            Es = paginator.page(page)
        except PageNotAnInteger:
            Es = paginator.page(1)
        except EmptyPage:
            Es = paginator.page(paginator.num_pages)
    
    return render(request, 'event/event-index.html', {
        'Es':Es,
        'title':'Snafu - Events'
    })

@login_required
def EaddRef(request):
    """
    Add a reference to DB.
    In POST method only, else raise 403.
    This view is used by AJAX.
    """
    if request.method == 'GET' : raise HttpResponseForbidden

    E = Event.objects.get(pk=request.POST['eventPk'])

    if request.POST['form_type'] == 'big' :
        form = ReferenceBigForm

    elif request.POST['form_type'] == 'host' :
        form = HostReferenceForm

    form = form(request.POST)
    if form.is_valid() :
        R = form.save()
    else :
        errors = json.dumps(form.errors)
        return HttpResponse(errors, mimetype='application/json')

    for status in ('WARNING','CRITICAL','UNKNOWN','DOWN') :
        As = E.get_alerts().filter(host=form.data['host'], service=form.data['service'],status__name=status) 
        for _A in As: 
            _A.link_to_reference()

            A = E.get_primary_alert()
            if _A.isPrimary : 
                E.criticity = A.reference.mail_criticity.name
                E.save()

    return render(request, 'event/event-index.html', {
    })
