from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
import django.utils.simplejson as json

from sendim.models import Alert, MailTemplate
from sendim.forms import *
from referentiel.forms import *
from referentiel.defs import *
from referentiel.models import Host, Reference, Traduction

from re import match

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
def confManager(request, action, model, object_id=0) :
    if model == "glpiUser" :
        temp_dir = 'configuration/glpi/users/'
        Model = GlpiUser
        form = GlpiUserForm
        element_key = 'GU'
        filter_key = 'GUs'
        page_key = 'GUsPage'
        form_key = 'GlpiUserForm'

    elif model == "category" :
        temp_dir = 'configuration/glpi/categories/'
        Model = GlpiCategory
        form = GlpiCategoryForm
        element_key = 'C'
        filter_key = 'Cs'
        page_key = 'CsPage'
        form_key = 'GlpiCategoryForm'

    elif model == "host" :
        temp_dir = 'configuration/glpi/hosts/'
        Model = Host
        form = HostForm
        element_key = 'H'
        filter_key = 'Hs'
        page_key = 'HsPage'
        form_key = 'HostForm'

    elif model == "template" :
        temp_dir = 'configuration/mail/templates/'
        Model = MailTemplate
        form = MailTemplateForm
        element_key = 'MT'
        filter_key = 'MTs'
        page_key = 'MTsPage'
        form_key = 'MailTemplateForm'

    elif model == "mailGroup" :
        temp_dir = 'configuration/mail/groups/'
        Model = MailGroup
        form = MailGroupForm
        element_key = 'MG'
        filter_key = 'MGs'
        page_key = 'MGsPage'
        form_key = 'MailGroupForm'

    elif model == "mailType" :
        temp_dir = 'configuration/mail/types/'
        Model = MailType
        form = MailTypeForm
        element_key = 'MTy'
        filter_key = 'MTys'
        page_key = 'MTysPage'
        form_key = 'MailTypeForm'

    elif model == "user" :
        temp_dir = 'configuration/user/'
        Model = User
        form = UserForm
        element_key = 'U'
        filter_key = 'Us'
        page_key = 'UsPage'
        form_key = 'UserForm'

    else : raise Http404


    if action == 'list' :
        Objs = Model.objects.all()
        temp_file = 'ul.html'

        if match(r"(glpiUser|category|host|mailGroup|mailType)",model) :
            Objs = Objs.filter(name__icontains=request.GET['q'])

        if model == "template" :
            Objs = list( (
              set( Objs.filter(subject__icontains=request.GET['q']) ) |
              set( Objs.filter(body__icontains=request.GET['q']) ) |
              set( Objs.filter(comment__icontains=request.GET['q']) )
            ) )

        elif model == "mailGroup" :
            Objs = list( (
              set( MGs.filter(to__icontains=request.GET['q']) ) |
              set( MGs.filter(ccm__icontains=request.GET['q']) ) |
              set( MGs.filter(cc__icontains=request.GET['q']) )
            ) )

        Objs = Paginator(Objs, 10).page(request.GET.get('page',1))

        return render(request, temp_dir+temp_file, {
          page_key : Objs
        })

    elif action == 'get' :
        if model  == "glpiUser" : temp_file = 'user.html'
        elif model  == "user" : temp_file = 'user.html'
        elif model  == "category" : temp_file = 'category.html'
        elif model  == "host" : temp_file = 'host.html'
        elif model  == "template" : temp_file = 'template.html'
        elif model  == "mailGroup" : temp_file = 'group.html'
        elif model  == "mailType" : temp_file = 'type.html'

        return render(request, temp_dir+temp_file, {
           element_key : get_object_or_404(Model, pk=object_id)
        })

    elif action == 'form' :
        form = form()
        return render(request, temp_dir+'/form.html', {
          form_key : form
        })

    elif action == 'del' :
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

    else : raise Http404

    return render(request, temp_dir+temp_file, {
        filter_key : Model.objects.all()
    })

