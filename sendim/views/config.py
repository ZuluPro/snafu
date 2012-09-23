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
            service = Service.objects.get(service=request.POST['service'])
            for status in ('WARNING','CRITICAL','UNKNOWN') :
                status = Status.objects.get(pk=request.POST['id_'+status.lower()])
                T = Traduction(service=service, status=status, traduction=traduction)
                T.save()
                logprint("Save Traduction #"+str(T.pk), "green")

    return render(request, 'configuration/index.html', {
        'alerts':Alert.objects.all(),
        'alertsWithoutRef':Alert.objects.filter(reference=None),
        'alertsWithoutTrad':Alert.objects.filter(traduction=None),
        'references':Reference.objects.all(),
        'referenceForm':ReferenceForm,
        'traductions':Traduction.objects.all(),
        'traductionForm':TraductionForm,
        'traductionBigForm':TraductionBigForm,
        'mailTemplates':MailTemplate.objects.all(),
        'title':'Snafu - Configuration'
    })
