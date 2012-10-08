from django import template

from sendim.models import *
from referentiel.models import Reference

from referentiel.defs import getReference

register = template.Library()

@register.filter(name='getEscalation')
def getEscalation(value, arg=None) :
    A = Event.objects.get(pk=value).getPrimaryAlert() 

    R = A.reference

    if R : return R.escalation_contact
    else : return None
