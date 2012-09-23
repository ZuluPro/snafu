from django.shortcuts import render

from sendim.defs import *
from sendim.models import *
from referentiel.models import *
from referentiel.forms import *

from common import logprint

def configuration(request) :

    return render(request, 'configuation.html', {
        'subjects':MailSubject.objects.all()
        'bodies':MailBody.objects.all()
        'title':'Snafu - Configuration'
    })
