from django import template

from sendim.models import *
from referentiel.models import Reference

register = template.Library()

@register.filter(name='getProcedure')
def getProcedure(value, arg=None) :
    try:
        E = Event.objects.get(pk=value)
	A = E.getPrimaryAlert()
	R = A.reference
	return R.procedure
    except : pass
