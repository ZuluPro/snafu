from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
 
from sendim.defs import *
from sendim.forms import *
from referentiel.defs import *
from referentiel.models import MailGroup

@login_required
def getMailGroups(request) :
    """
    Get list of references filtered by host and service.
    Search GET['q'] in the 2 attributes and make a logical OR.
    
    Includes a Paginator which split references into pages of 10.

    This view is used with AJAX and return references' tabs.
    """
    MGs = MailGroup.objects.all()
    if request.GET['q'] :
        MGs = list( (
            set( MGs.filter(mail_group__icontains=request.GET['q']) ) |
            set( MGs.filter(to__icontains=request.GET['q']) ) |
            set( MGs.filter(ccm__icontains=request.GET['q']) ) |
            set( MGs.filter(cc__icontains=request.GET['q']) )
        ) )
    MGs = Paginator(MGs, 10).page(request.GET.get('page',1))
    return render(request, 'configuration/mail/groups/ul.html', {
        'MGsPage':MGs
    })

@login_required
def mailGroup(request, mgroup_id, action="get") :
    """
    Get or delete a reference.

    Delete :
     - Return references count for put it in page.

    This view is used with AJAX.
    """
    if action == "get" :
        return render(request, 'configuration/mail/groups/group.html', {
           'MG':get_object_or_404(MailGroup, pk=mgroup_id)
        })

    elif action == "del" :
        MG = get_object_or_404(MailGroup, pk=mgroup_id)
        MG.delete()
 
    elif action == "add" :
         Form = MailGroupForm(request.POST)
         if Form.is_valid() :
             Form.save()
         
    return render(request, 'configuration/mail/groups/tabs.html', {
        'MGs':MailGroup.objects.all()
    })

@login_required
def getMailGroupForm(request,mgroup_id=0) :
    """
    Create a BigForm for a given alert.
    If alert_id is 0, it creates an empty form.

    This view is used with AJAX.
    """
    
    Form = MailGroupForm()
    return render(request, 'configuration/mail/groups/form.html', {
         'MailGroupForm':Form
    })

