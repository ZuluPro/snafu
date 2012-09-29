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

def EaddRef(request):
    E = Event.objects.get(pk=request.POST['eventPk'])
    A = E.getPrimaryAlert()
    host = Host.objects.get(pk=request.POST['form-0-host'])
    service = Service.objects.get(pk=request.POST['form-0-service'])
    POST = {}
    for k,v in request.POST.items() :
        if 'form-' in k :
            POST[k[7:]] = v

    for status in ('WARNING','CRITICAL','UNKNOWN') :
        if not Reference.objects.filter(host=host,service=service,status__status=status) :
            R = Reference(
                host = host,
                service = service,
                status = Status.objects.get(status=status),

                escalation_contact = POST['escalation_contact'],
                tendancy = POST['tendancy'],
                outage = POST['outage'],
                explanation = POST['explanation'],
                origin = POST['origin'],
                procedure = POST['procedure'],

                mail_type = MailType.objects.get(pk=POST['mail_type']),
                mail_group = MailGroup.objects.get(pk=POST['mail_group']),

                glpi_category = GlpiCategory.objects.get(pk=POST['glpi_category']),
                glpi_source = POST['glpi_source'],
                glpi_dst_group = GlpiGroup.objects.get(pk=POST['glpi_dst_group']),
                glpi_supplier = GlpiSupplier.objects.get(pk=POST['glpi_supplier'])
            )
            R.mail_criticity = MailCriticity.objects.get(pk=POST[status.lower()+'_criticity'])
            R.glpi_urgency = GlpiUrgency.objects.get(pk=POST[status.lower()+'_urgency'])
            R.glpi_priority = GlpiPriority.objects.get(pk=POST[status.lower()+'_priority'])
            R.glpi_impact = GlpiImpact.objects.get(pk=POST[status.lower()+'_impact'])
            R.save()

    for A in Alert.objects.filter(host=host,service=service,reference=None): A.linkToReference()
    E.criticity = E.getPrimaryAlert().reference.mail_criticity.mail_criticity
    E.save()

    return render(request, 'event/event-index.html', {
    })
