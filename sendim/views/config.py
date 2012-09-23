from django.shortcuts import render

from sendim.defs import *
from sendim.models import *
from referentiel.models import *
from referentiel.forms import *

from common import logprint

def configuration(request) :

    return render(request, 'configuration/index.html', {
        'alerts':Alert.objects.all(),
        'alertsWithoutRef':Alert.objects.filter(reference=None),
        'alertsWithoutTrad':Alert.objects.filter(traduction=None),
        'references':Reference.objects.all(),
        'traductions':Traduction.objects.all(),
        'subjects':MailSubject.objects.all(),
        'bodies':MailBody.objects.all(),
        'title':'Snafu - Configuration'
    })
