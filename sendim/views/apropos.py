from django.shortcuts import render
from django.conf import settings

def apropos(request) :
    with open(settings.BASEDIR+'/../LICENSE') as text :
        license = text.read()
    return render(request, 'apropos.html', {
        'license':license
    } )
