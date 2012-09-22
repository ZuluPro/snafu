from django import template

from sendim.models import *
from referentiel.models import Reference

from referentiel.defs import getReference

register = template.Library()

@register.filter(name='getEscalation')
def getEscalation(value, arg=None) :
    A = Alert.objects.order_by('-pk').filter(event__pk__exact=value).exclude(status__status__exact='OK')[0]
    R = getReference(A)
    if R == None : return None 
    return R.escalation_contact
