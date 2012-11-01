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
     - Hosts
     - GLPI categories
    """
    
    Rs = Reference.objects.all()
    RsPage = Paginator(Rs, 10).page(1)

    Ts = Traduction.objects.all()
    TsPage = Paginator(Ts, 10).page(1)
    AsWithoutTrad = Alert.objects.filter( Q(traduction=None), ~Q(status__status='OK'), ~Q(status__status='UP'), ~Q(status__status='DOWN') )
    AsWithoutTradPage = Paginator(AsWithoutTrad, 10).page(1)

    Us = User.objects.all()
    UsPage = Paginator(Us, 10).page(1)

    Hs = Host.objects.all()
    HsPage = Paginator(Hs, 10).page(1)

    Cs = GlpiCategory.objects.all()
    CsPage = Paginator(Cs, 10).page(1)

    MTs = MailTemplate.objects.all()
    MTsPage = Paginator(MTs, 10).page(1)

    MGs = MailGroup.objects.all()
    MGsPage = Paginator(MGs, 10).page(1)

    return render(request, 'configuration/index.html', {
        'Rs':Rs,
        'RsPage':RsPage,
        'AsWithoutRef':Alert.objects.filter( Q(reference=None), ~Q(status__status='OK'), ~Q(status__status='UP'), ~Q(status__status='DOWN') ),
        'referenceBigForm':ReferenceBigForm,

        'Ts':Ts,
        'TsPage':TsPage,
        'traductionBigForm':TraductionBigForm,
        'AsWithoutTrad':AsWithoutTrad,
        'AsWithoutTradPage':AsWithoutTradPage,

        'Us':Us,
        'UsPage':UsPage,
        'UserForm':UserForm,

        'Hs':Hs,
        'HsPage':HsPage,

        'Cs':Cs,
        'CsPage':CsPage,

        'MTs':MTs,
        'MTsPage':MTsPage,

        'MGs':MGs,
	'MGsPage':MGsPage,

        'title':'Snafu - Configuration'
    })

