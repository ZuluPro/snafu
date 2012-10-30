from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
 
from sendim.defs import *
from sendim.forms import *
from referentiel.defs import *
from sendim.models import MailTemplate

@login_required
def getMailTemplates(request) :
    """
    Get list of references filtered by host and service.
    Search GET['q'] in the 2 attributes and make a logical OR.
    
    Includes a Paginator which split references into pages of 10.

    This view is used with AJAX and return references' tabs.
    """
    MTs = MailTemplate.objects.all()
    if request.GET['q'] :
        MTs = list( (
            set( MTs.filter(subject__icontains=request.GET['q']) ) |
            set( MTs.filter(body__icontains=request.GET['q']) ) |
            set( MTs.filter(comment__icontains=request.GET['q']) )
        ) )
    MTs = Paginator(MTs, 10).page(request.GET.get('page',1))
    return render(request, 'configuration/mail/templates/ul.html', {
        'MTsPage':MTs
    })

@login_required
def mailTemplate(request, temp_id, action="get") :
    """
    Get or delete a reference.

    Delete :
     - Return references count for put it in page.

    This view is used with AJAX.
    """
    if action == "get" :
        return render(request, 'configuration/mail/templates/template.html', {
           'MT':get_object_or_404(MailTemplate, pk=temp_id)
        })

    elif action == "del" :
        MT = get_object_or_404(MailTemplate, pk=temp_id)
        MT.delete()
 
    elif action == "add" :
         Form = MailTemplateForm(request.POST)
         if not Form.is_valid() :
             Form.save()
         
    return render(request, 'configuration/mail/templates/tabs.html', {
        'MTs':MailTemplate.objects.all()
    })

@login_required
def getMailTemplateForm(request,temp_id=0) :
    """
    Create a BigForm for a given alert.
    If alert_id is 0, it creates an empty form.

    This view is used with AJAX.
    """
    
    Form = MailTemplateForm(data)
    return render(request, 'configuration/mail/templates/form.html', {
         'referenceBigForm':Form
    })

