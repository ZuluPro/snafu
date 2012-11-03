from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib import messages

from sendim.defs import *
from sendim.models import *
from sendim.forms import *
from sendim.exceptions import UnableToConnectGLPI,UnableToConnectNagios
from referentiel.models import *
from referentiel.forms import *
from referentiel.defs import *

from common import logprint

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
            A = E.getPrimaryAlert()

        if 'reloadAlert_q' in request.POST :
            try : 
                newAs = reloadAlert()
                if newAs :
                    messages.add_message(
                      request,
                      messages.SUCCESS,
                      u"<b>Lecture des unit\xe9s de supervision</b> : Effectu\xe9<br>"+''.join( [ u"<li>Cr\xe9ation de l'Alerte #"+str(A.pk)+" dans l'Event #"+str(A.event.pk)+"</il>" for A in newAs ] )
                    )
                else : messages.add_message(request,messages.INFO,u"<b>Lecture des unit\xe9s de supervision</b> : Effectu\xe9<br>Aucune nouvelle alerte." )
            except UnableToConnectNagios, e :
                messages.add_message(request,messages.ERROR,u"<b>Connexion \xe0 Nagios impossible</b>")

        elif "sendmail_q" in request.POST :
            if sendMail( request.POST ) :
                messages.add_message(request,messages.SUCCESS,u"Envoi d'un mail pour l'\xe9v\xe9nement #"+str(E.pk)+"." )
                logprint("Mail sent for Event #"+str(eventPk) )

        elif "treatment_q" in request.POST :
	    if E.criticity == '?' or not E.getPrimaryAlert().reference : 
		
		Forms = getFormSet(E)
		return render(request, 'event/add-reference.html', {
			'Forms':Forms, 'E':E,
        		'title':'Snafu - Ajout de Reference'
		} )

            if not E.glpi :
               try :
                   E.glpi = createTicket(E)
                   messages.add_message(request,messages.SUCCESS,"Ticket #"+str(E.glpi)+u" associ\xe9 \xe0 Event #"+str(E.pk))
               except UnableToConnectGLPI :
                   messages.add_message(request,messages.ERROR,u"Impossible de se connecter \xe0 GLPI.")
                   return redirect('/snafu/events')

            # Constitution du mail
            msg = makeMail(E)

            # Recuperation des graphs correspondant
            graphList = readGraphs(E.element.name, A.service.name)
    
            # Envoi du formulaire d'envoi de mail
            return render(request,'event/preview-mail.html', {
                    'msg':msg,
                    'E':E,
                    'graphList':graphList,
                    'title':'Snafu - Envoi de mail'
            })
        Es = Event.objects.filter(closed=False).order_by('-pk')
    else :
        Es = Event.objects.filter(closed=False).order_by('-pk')

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

    host,service = postFormSet(request.POST)

    for status in ('WARNING','CRITICAL','UNKNOWN') :
        As = E.getAlerts().filter(status__name=status) 
        for _A in As: 
            _A.linkToReference()

            A = E.getPrimaryAlert()
            if _A.isPrimary : 
                E.criticity = A.reference.mail_criticity.mail_criticity
                E.save()

    return render(request, 'event/event-index.html', {
    })
