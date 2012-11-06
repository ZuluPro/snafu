from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
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
    AsWithoutTrad = Alert.objects.filter( Q(traduction=None), ~Q(status__name='OK'), ~Q(status__name='UP'), ~Q(status__name='DOWN') )
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

    MTys = MailType.objects.all()
    MTysPage = Paginator(MTys, 10).page(1)

    GUs = GlpiUser.objects.all()
    GUsPage = Paginator(GUs, 10).page(1)

    return render(request, 'configuration/index.html', {
        'Rs':Rs,
        'RsPage':RsPage,
        'AsWithoutRef':Alert.objects.filter( Q(reference=None), ~Q(status__name='OK'), ~Q(status__name='UP'), ~Q(status__name='DOWN') ),
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

        'MTys':MTys,
	'MTysPage':MTysPage,

        'GUs':GUs,
	'GUsPage':GUsPage,

        'title':'Snafu - Configuration'
    })

@login_required
def confManager(request, object, action, object_id=0) :
    print object, action
    if object == "glpiUser" :
        temp_dir = 'configuration/glpi/users/'
        Model = GlpiUser
        form = GlpiUserForm
        element_key = 'GU'
        filter_key = 'GUs'
        page_key = 'GUsPage'

    if action == 'list' :
        Objs = Model.objects.all()
        temp_file = 'ul.html'

        if object == "glpiUser" :
            if request.GET['q'] :
                Objs = Objs.filter(name__icontains=request.GET['q'])

        Objs = Paginator(Objs, 10).page(request.GET.get('page',1))

        return render(request, temp_dir+temp_file, {
          page_key : Objs
        })

    elif action == 'get' :
        if object == "glpiUser" : temp_file = 'user.html'

        return render(request, temp_dir+temp_file, {
           element_key : get_object_or_404(Model, pk=object_id)
        })

    elif action == 'delete' :
        temp_file = 'tabs.html'
        Obj = get_object_or_404(Model, pk=object_id)
        Obj.delete()

    elif action == "add" :
         form = form(request.POST)
         if form.is_valid() :
             form.save()
         else :
             errors = json.dumps(form.errors)
             return HttpResponse(errors, mimetype='application/json')

    return render(request, temp_dir+temp_file, {
        filter_key : Model.objects.all()
    })

