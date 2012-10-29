from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from referentiel.models import GlpiCategory
from referentiel.forms import GlpiCategoryForm
#from sendim.defs import get_categories_from_glpi

@login_required
def getCategories(request) :
    """
    Get list of category filtered by their names.
    
    Includes a Paginator which split references into pages of 10.

    This view is used with AJAX and return categories' tabs.
    """
    Cs = GlpiCategory.objects.all()
    if request.GET['q'] :
        Cs = Cs.filter(glpi_category__icontains=request.GET['q'])  
    Cs = Paginator(Cs, 10).page(request.GET.get('page',1))

    return render(request, 'configuration/glpi/categories/ul.html', {
        'CsPage':Cs
    })

@login_required
def category(request, cat_id, action="get") :
    """
    Get, add or delete a category.
        
    Delete :
     - Return GlpiCategory count for put it in page.

    This view is used with AJAX.
    """
    if action == "get" :
        return render(request, 'configuration/glpi/categories/category.html', {
           'C':get_object_or_404(GlpiCategory, pk=cat_id)
        })  
            
    elif action == "del" :
        C = get_object_or_404(GlpiCategory, pk=cat_id)
        C.delete()
    
    elif action == "add" :
         Form = GlpiCategoryForm(request.POST)
         if Form.is_valid() :
             Form.save()
         
    return render(request, 'configuration/glpi/categories/tabs.html', {
        'Cs':GlpiCategory.objects.all(),
    })

#@login_required
#def categoryDiff(request) :
#    """
#    Make a diff for host between DB and GLPI.
#    Return a table with : 
#     - Hosts in project's DB
#     - Hosts in GLPI's DB
#     - Hosts without id
#     - Hosts with id have changed
#     - Hosts which is in project's DB but not in GLPI
#     - Hosts which is in GLPI's DB but not in project's one
#    """
#
#    db_hosts = [ (H.host,H.glpi_id.__int__()) for H in Host.objects.all() if H.glpi_id ]
#    glpi_hosts = [ (H['name'],int(H['id'])) for H in get_hosts_from_glpi() ]
#    no_id = [ (H.host,0) for H in Host.objects.filter(glpi_id=None) ]
#    bad_id = list()
#    not_in_glpi = ( set(db_hosts) ^ set(glpi_hosts) ) & set(db_hosts)
#    not_in_db = ( set(db_hosts) ^ set(glpi_hosts) ) & set(glpi_hosts)
#
#    diff = {}
#    diff['db'] = Host.objects.all()
#    diff['glpi'] = glpi_hosts
#    diff['no_id'] = no_id
#    diff['bad_id'] = bad_id
#    diff['not_in_glpi'] = not_in_glpi
#    diff['not_in_db'] = not_in_db
#
#    return render(request, 'configuration/glpi/hosts/diff.html', {
#        'diff':diff
#    })

@login_required
def getGlpiCategoryForm(request) :
    """
    Create a form
    This view is used with AJAX.
    """

    Form = GlpiCategoryForm()
    return render(request, 'configuration/glpi/categories/form.html', {
         'GlpiCategoryForm':Form
    })

