from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect

from sendim.defs import *
from sendim.models import *
from sendim.forms import *
from referentiel.models import *
from referentiel.forms import *
from referentiel.defs import *

from common import logprint

@login_required
def events(request) :
    """List events and do processing on them.
    
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
            treatAlerts()

        elif "sendmail_q" in request.POST :
            sendMail( request.POST )
            logprint("Mail sent for Event #"+str(eventPk) )

        elif "treatment_q" in request.POST :
	    if E.criticity == '?' or not E.getPrimaryAlert().reference : 
		
		Forms = getFormSet(E)
		return render(request, 'event/add-reference.html', {
			'Forms':Forms, 'E':E,
        		'title':'Snafu - Ajout de Reference'
		} )

            if not E.glpi :
               E.glpi = createTicket(eventPk)
               if not E.glpi : redirect('/snafu/events')

            # Constitution du mail
            msg = makeMail(E)

            # Recuperation des graphs correspondant
            graphList = readGraphs(E.element.host, A.service.service)
    
            # Envoi du formulaire d'envoi de mail
            return render(request,'event/preview-mail.html', {
                    'msg':msg,
                    'E':E,
                    'graphList':graphList,
                    'title':'Snafu - Envoi de mail'
            })
    return render(request, 'event/event-index.html', {
        'Es':Event.objects.filter(closed=False).order_by('-pk'),
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
        As = E.getAlerts().filter(status__status=status) 
        for _A in As: 
            _A.linkToReference()

            A = E.getPrimaryAlert()
            if A.isPrimary : 
                E.criticity = A.reference.mail_criticity.mail_criticity
                E.save()

    return render(request, 'event/event-index.html', {
    })
