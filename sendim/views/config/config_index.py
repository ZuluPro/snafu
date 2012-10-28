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
    RsPage = Paginator(Rs, 10).page(1)

    Ts = Traduction.objects.all()
    TsPage = Paginator(Ts, 10).page(1)

    AsWithoutTrad = Alert.objects.filter( Q(traduction=None), ~Q(status__status='OK'), ~Q(status__status='UP') )
    AsWithoutTradPage = Paginator(AsWithoutTrad, 10).page(1)

    return render(request, 'configuration/index.html', {
        'Rs':Rs,
        'RsPage':RsPage,
        'AsWithoutRef':Alert.objects.filter( Q(reference=None), ~Q(status__status='OK'), ~Q(status__status='UP') ),
        'referenceBigForm':ReferenceBigForm,

        'Ts':Ts,
        'TsPage':TsPage,
        'traductionBigForm':TraductionBigForm,
        'AsWithoutTrad':Alert.objects.filter( Q(traduction=None), ~Q(status__status='OK'), ~Q(status__status='UP') ),
        'AsWithoutTradPage':AsWithoutTradPage,

        'mailTemplates':MailTemplate.objects.all(),
        'mailTemplateForm':MailTemplateForm,

        'Us':User.objects.all(),
        'UserForm':UserForm,

        'hosts':Host.objects.filter(glpi_id=None),
        'title':'Snafu - Configuration'
    })

