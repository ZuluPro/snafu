from django import template

from sendim.models import *
from referentiel.models import Reference

from referentiel.defs import getReference

register = template.Library()

@register.filter(name='getEscalation')
def getEscalation(value, arg=None) :
    As = Alert.objects.order_by('-pk').filter(event__pk__exact=value).exclude(Q(status__status__exact='OK') | Q(status__status__exact='UP'))
    if not As : return None

    R = getReference(As[0])
    if not None : return None 

    return R.escalation_contact
