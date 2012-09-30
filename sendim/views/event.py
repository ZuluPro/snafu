from django.forms.formsets import formset_factory
from django.shortcuts import render

from sendim.defs import *
from sendim.models import *
from sendim.forms import *
from referentiel.models import *
from referentiel.forms import *
from referentiel.defs import *

from common import logprint

def events(request) :
    if request.method == 'POST' :

        if 'reloadAlert_q' in request.POST :
            treatAlerts()

        if 'agregate_q' in request.POST :
            agregate(request.POST.getlist('toAgr'), request.POST['choicedEvent'], request.POST['message'] )

        if 'alertPk' in request.POST :
            alertPk = request.POST["alertPk"]
            A = Alert.objects.get(pk=alertPk)
        if 'eventPk' in request.POST :
                eventPk = request.POST["eventPk"]
                E = Event.objects.get(pk=eventPk)
		A = E.getPrimaryAlert()

        if "add_ref_q" in request.POST :
		#ReferenceBigFormSet = formset_factory(ReferenceBigForm, extra=0 )
		#Forms = ReferenceBigFormSet(initial= [{
		#   'host':E.element.pk, 'service':E.getPrimaryAlert().service,
		#		'glpi_source':'Supervision'
		#}])
		Forms = makeMultipleForm( createServiceList(E.getAlerts() ) )#ReferenceBigFormSet(initial= [{
		return render(request, 'reference.form.html', {
			'Forms':Forms, 'E':E
		} )

            

        if "sendmail_q" in request.POST :
            sendMail( request.POST )
            logprint("Mail sent for Event #"+str(eventPk) )

        elif "treatment_q" in request.POST :
	    if E.criticity == '?' or not E.getPrimaryAlert().reference : 
		
		Forms = makeMultipleForm( createServiceList(E.getAlerts() ) )#ReferenceBigFormSet(initial= [{
		return render(request, 'reference.form.html', {
			'Forms':Forms, 'E':E,
        		'title':'Snafu - Ajout de Reference'
		} )

            if not E.glpi : E.glpi = createTicket(eventPk)

            # Constitution du mail
            msg = makeMail(E)

            # Recuperation des graphs correspondant
            graphList = readGraphs(E.element.host, A.service.service)
    
            # Envoi du formulaire d'envoi de mail
            return render(request,'sendim.mail.html', {
                    'msg':msg,
                    'E':E,
                    'graphList':graphList,
                    'title':'Snafu - Envoi de mail'
            })
    return render(request, 'events.html', {
        'Es':Event.objects.filter(closed=False).order_by('-pk'),
        'title':'Snafu - Events'
    })

def eventsAgr(request) :

    return render(request, 'events-agr.html', {
        'events': [ Event.objects.get(pk=pk) for pk in request.GET.getlist('events[]') ][::-1],
        'alerts': Alert.objects.order_by('-date')
    })

