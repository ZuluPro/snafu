from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
 
from sendim.models import Alert
from referentiel.models import Reference
from referentiel.forms import ReferenceForm, HostReferenceForm, ReferenceBigForm

@login_required
def getReferences(request) :
    """
    Get list of references filtered by host and service.
    Search GET['q'] in the 2 attributes and make a logical OR.
    
    Includes a Paginator which split references into pages of 10.

    This view is used with AJAX and return references' tabs.
    """
    from django.core.paginator import Paginator

    Rs = Reference.objects.all()
    if request.GET['q'] :
        Rs = list( (
            set( Rs.filter(host__name__icontains=request.GET['q']) ) |
            set( Rs.filter(service__name__icontains=request.GET['q']) )
        ) )
    Rs = Paginator(Rs, 10).page(request.GET.get('page',1))
    return render(request, 'configuration/reference/refs/ul.html', {
        'RsPage':Rs
    })

@login_required
def reference(request, ref_id, action="get") :
    """
    Get or delete a reference.

    Delete :
     - Return references count for put it in page.

    This view is used with AJAX.
    """
    if action == "get" :
        return render(request, 'configuration/reference/refs/ref.html', {
           'R':get_object_or_404(Reference, pk=ref_id)
        })

    elif action == "del" :
        R = get_object_or_404(Reference, pk=ref_id)
        R.delete()
 
    elif action == "add" :
         form = ReferenceBigForm(request.POST)
         if form.is_valid() :
             form.save()
         
    return render(request, 'configuration/reference/tabs.html', {
        'Rs':Reference.objects.all(),
        'AsWithoutRef':Alert.objects.get_without_reference()
    })

@login_required
def getAlertWithoutRef(request,alert_id) :
    """Get a single alert informations."""
    return render(request, 'configuration/reference/alerts/alert.html', {
        'A':get_object_or_404(Alert, pk=alert_id)
    })

@login_required
def getAsWithoutRef(request) :
    """Get references filtered by host and service."""
    As = Alert.objects.get_without_reference()
    if request.GET['q'] :
        As = (
            set( As.filter(host__name__icontains=request.GET['q']) ) |
            set( As.filter(service__name__icontains=request.GET['q']) )
        )
    return render(request, 'configuration/reference/alerts/ul.html', {
        'AsWithoutRef':As
    })

@login_required
def getRefForm(request,_type='simple') :
    
    if _type == 'simple' : Form = ReferenceForm()
    elif _type == 'host' : Form = HostReferenceForm()
    elif _type == 'big' : Form = ReferenceBigForm()

    return render(request, 'configuration/reference/form.html', {
         'ReferenceForm':Form,
         'FormType':type(Form)
    })

@login_required
def addReference(request, ref_id=0) :
    """
    Get or delete a reference.

    Delete :
     - Return references count for put it in page.

    This view is used with AJAX.
    """
    import django.utils.simplejson as json
    from django.http import HttpResponse

    if request.POST['form_type'] == 'simple' : Form = ReferenceForm(request.POST)
    elif request.POST['form_type'] == 'host' : Form = HostReferenceForm(request.POST)
    elif request.POST['form_type'] == 'big' : Form = ReferenceBigForm(request.POST)
    else : Form = ReferenceForm(request.POST)

    if Form.is_valid() :
        Form.save()
    else :
        errors = json.dumps(Form.errors)
        return HttpResponse(errors, mimetype='application/json')
         
    return render(request, 'configuration/reference/tabs.html', {
        'Rs':Reference.objects.all(),
        'AsWithoutReference':Alert.objects.get_without_reference()
    })



