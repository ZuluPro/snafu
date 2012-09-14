from django.shortcuts import render

from sendim.defs import *
from sendim.models import *
from sendim.forms import *
from referentiel.forms import *
from referentiel.models import *
from referentiel.forms import *

from common import logprint

def configuration(request) :
    
    if request.method == 'POST' :
        if request.POST['action'] == 'addTrad' :
            service = Service.objects.get(pk=request.POST['service'])
            for status in ('WARNING','CRITICAL','UNKNOWN') :
                traduction = request.POST[status.lower()]
                status = Status.objects.get(status=status)
                if not Traduction.objects.filter(service=service, status=status) :
                    T = Traduction(service=service, status=status, traduction=traduction)
                    T.save()
                    logprint("Save Traduction #"+str(T.pk), "green")
            if 'apply' in request.POST :
                for A in Alert.objects.filter(service=service,traduction=None) :
                    A.linkToTraduction()
                    

        elif request.POST['action'] == 'addRef' :
            POST = dict( request.POST.items() )
	    for k,v in POST.items() :
                if 'form-' in k :
                    POST[k[7:]] = v
                    del POST[k]

            host = Host.objects.get(pk=POST['host'])
            service = Service.objects.get(pk=POST['service'])
            for status in ('WARNING','CRITICAL','UNKNOWN') :
                R = Reference(
                    host = host,
                    service = service,
                    status = Status.objects.get(status=status.lower()),

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
                    glpi_supplier = GlpiSupplier.objects.get(pk=POST['glpi_supplier']),
                )
                R.mail_criticity = MailCriticity.objects.get(pk=POST[status.lower()+'_criticity'])
                R.glpi_urgency = GlpiUrgency.objects.get(pk=POST[status.lower()+'_urgency'])
                R.glpi_priority = GlpiPriority.objects.get(pk=POST[status.lower()+'_priority'])
                R.glpi_impact = GlpiImpact.objects.get(pk=POST[status.lower()+'_impact'])
                R.save()


                if 'apply' in request.POST :
                    for A in Alert.objects.filter(host=host, service=service,reference=None) :
                        A.linkToReference()

	    if 'treatment_q' in request.POST :
		    print request.POST
                    E = Event.objects.get(pk=request.POST['eventPk'])
                    E.criticity = R.mail_criticity.mail_criticity
                    E.save()
                    A = E.getPrimaryAlert()
                    A.reference = R
                    A.save()

    return render(request, 'configuration/index.html', {
        'alerts':Alert.objects.all(),
        'alertsWithoutRef':Alert.objects.filter(reference=None),
        'alertsWithoutTrad':Alert.objects.filter(traduction=None),
        'references':Reference.objects.all(),
        'referenceForm':ReferenceForm,
        'referenceBigForm':ReferenceBigForm,
        'traductions':Traduction.objects.all(),
        'traductionForm':TraductionForm,
        'traductionBigForm':TraductionBigForm,
        'mailTemplates':MailTemplate.objects.all(),
        'mailTemplateForm':MailTemplateForm,
        'title':'Snafu - Configuration'
    })
