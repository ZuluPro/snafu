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
            host = Host.objects.get(pk=request.POST['host'])
            service = Service.objects.get(pk=request.POST['service'])
            for status in ('WARNING','CRITICAL','UNKNOWN') :
                R = Reference(
                    host = host,
                    service = service,
                    status = Status.objects.get(status=status.lower()),

                    escalation_contact = request.POST['escalation_contact'],
                    tendancy = request.POST['tendancy'],
                    outage = request.POST['outage'],
                    explanation = request.POST['explanation'],
                    origin = request.POST['origin'],
                    procedure = request.POST['procedure'],
                
                    mail_type = MailType.objects.get(pk=request.POST['mail_type']),
                    mail_group = MailGroup.objects.get(pk=request.POST['mail_group']),
                
                    glpi_category = GlpiCategory.objects.get(pk=request.POST['glpi_category']),
                    glpi_source = request.POST['glpi_source'],
                    glpi_dst_group = GlpiGroup.objects.get(pk=request.POST['glpi_dst_group']),
                    glpi_supplier = GlpiSupplier.objects.get(pk=request.POST['glpi_supplier']),
                )
                R.mail_criticity = MailCriticity.objects.get(pk=request.POST[status.lower()+'_criticity'])
                R.glpi_urgency = GlpiUrgency.objects.get(pk=request.POST[status.lower()+'_urgency'])
                R.glpi_priority = GlpiPriority.objects.get(pk=request.POST[status.lower()+'_priority'])
                R.glpi_impact = GlpiImpact.objects.get(pk=request.POST[status.lower()+'_impact'])
                R.save()

                if 'apply' in request.POST :
                    for A in Alert.objects.filter(host=host, service=service,reference=None) :
                        A.linkToReference()

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
        'title':'Snafu - Configuration'
    })
