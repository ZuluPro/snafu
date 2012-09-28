from django.forms.formsets import formset_factory
from django.shortcuts import render, redirect

from sendim.defs import *
from sendim.models import *
from sendim.forms import *
from referentiel.models import *
from referentiel.forms import *
from referentiel.defs import *

from common import logprint

def events(request) :
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
		
		Forms = makeMultipleForm( createServiceList(E.getAlerts() ) )
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

