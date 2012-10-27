from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q

from sendim.models import Alert, MailTemplate
from sendim.forms import *
from referentiel.defs import *
from referentiel.models import Host, Reference, Traduction

@login_required
def configuration(request) :
    """
    Index of configuration, this view is the only one which is request without AJAX.
    It gets all necessary data dor make menus:
     - References
     - Traductions
     - Mail templates
     - Users
    """
    
    Rs = Reference.objects.all()
    return render(request, 'configuration/index.html', {
        'hosts':Host.objects.filter(glpi_id=None),
        'AsWithoutRef':Alert.objects.filter( Q(reference=None), ~Q(status__status='OK'), ~Q(status__status='UP') ),
        'alertsWithoutTrad':Alert.objects.filter(traduction=None),
        'Rs':Rs,
        'referenceBigForm':ReferenceBigForm,
        'traductionBigForm':TraductionBigForm,
        'mailTemplates':MailTemplate.objects.all(),
        'mailTemplateForm':MailTemplateForm,
        'Us':User.objects.all(),
        'UserForm':UserForm,
        'title':'Snafu - Configuration'
    })

