from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render

from sendim.defs import *
from sendim.models import *
from sendim.forms import *
from referentiel.defs import *
from referentiel.forms import *
from referentiel.models import *

from common import logprint

@login_required
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

    return render(request, 'configuration/index.html', {
        'hosts':Host.objects.filter(glpi_id=None),
        'alerts':Alert.objects.all(),
        'AsWithoutRef':Alert.objects.filter(reference=None),
        'alertsWithoutTrad':Alert.objects.filter(traduction=None),
        'references':Reference.objects.all(),
        'referenceForm':ReferenceForm,
        'referenceBigForm':ReferenceBigForm,
        'traductions':Traduction.objects.all(),
        'traductionForm':TraductionForm,
        'traductionBigForm':TraductionBigForm,
        'mailTemplates':MailTemplate.objects.all(),
        'mailTemplateForm':MailTemplateForm,
        'Us':User.objects.all(),
        'UserForm':UserForm,
        'title':'Snafu - Configuration'
    })


