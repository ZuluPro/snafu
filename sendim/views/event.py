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

        if "create_ticket_q" in request.POST :
            ticketId = createTicket( eventPk, alertPk )
            logprint("Add ticket #" +str(ticketId)+ "to Event #" +str(eventPk), 'green')

        elif "add_ref_q" in request.POST :
		#ReferenceBigFormSet = formset_factory(ReferenceBigForm, extra=0 )
		#Forms = ReferenceBigFormSet(initial= [{
		#   'host':E.element.pk, 'service':E.getPrimaryAlert().service,
		#		'glpi_source':'Supervision'
		#}])
		Forms = makeMultipleForm( createServiceList(E.getAlerts() ) )#ReferenceBigFormSet(initial= [{
		return render(request, 'reference.form.html', {
			'Forms':Forms, 'E':E
		} )

            

        elif "sendmail_q" in request.POST :
            sendMail( request.POST )
            logprint("Mail sent for Event #"+str(eventPk) )

        elif "treatment_q" in request.POST :
	    if E.criticity == '?' or not E.getPrimaryAlert().reference : 
		
#		ReferenceBigFormSet = formset_factory(ReferenceBigForm, extra=0 )
		Forms = makeMultipleForm( createServiceList(E.getAlerts() ) )#ReferenceBigFormSet(initial= [{
#		   'host':E.element.pk, 'service':E.getPrimaryAlert().service,
#				'glpi_source':'Supervision'
#		}])
		return render(request, 'reference.form.html', {
			'Forms':Forms, 'E':E
		} )

            if not E.glpi : E.glpi = createTicket(eventPk)

            # Constitution du mail
            msg = makeMail(E)

            # Recuperation des graphs correspondant
            graphList = readGraphs(E.element.host, A.service.service)
    
            # Envoi du formulaire d'envoi de mail
            return render(request,'sendim.mail.html', {
                    'msg':msg,
                    'alert':A,
                    'event':E,
                    'graphList':graphList
            })
    return render(request, 'events.html', {
        'events':Event.objects.order_by('-pk'),
        'alerts':Alert.objects.all(),
        'title':'Snafu - Events'
    })


def createMail(request):
	E = Event.objects.get( pk=request.POST['eventPk'])
	A = Alert.objects.get(pk=request.POST['alertPk'])
	# Recherche du MailGroup correspondant
	R = Reference.objects.filter(host__host__exact=A.host.host, service__service__exact=A.service.service, status__status__exact=A.status.status )[0]

	# Constitution du mail
	msg = {} 
	msg['from'] = "Equipe d'exploitation Autolib' <it-prod@autolib.eu>"
	msg['to'] = R.mail_group.to
	if E.criticity == 'Majeur' : msg['to'] += ', '+ R.mail_group.ccm
	msg['cc'] = ' ,'.join( [ 'it-prod@autolib.eu', R.mail_group.cc] )
	msg['subject'] = '[Incident '+R.mail_type.mail_type+' Autolib\' - '+E.criticity+'] '+E.date.strftime('%d/%m/%y')+' - '+ E.message +' sur ' +E.element.host +' - GLPI '+str(E.glpi)
	with open('./mailforhost.txt' , 'r') as mailFile : msg['body'] = mailFile.read()
	
	# Recuperation des graphs correspondant
        graphList = readGraphs(E.element.host, A.service.service)

	# Envoi du formulaire d'envoi de mail
	return render(request, 'sendim.mail.html', {
		'msg':msg,
		'alert':A,
		'event':E, 'graphList':graphList,
                'title':'Snafu - Envoi de mail'
	})

def eventsAgr(request) :

    return render(request, 'events-agr.html', {
        'events': [ Event.objects.get(pk=pk) for pk in request.GET.getlist('events[]') ][::-1],
        'alerts': Alert.objects.order_by('-date')
    })

