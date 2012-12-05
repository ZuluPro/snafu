from django import template

from sendim.models import *
from referentiel.models import Reference

register = template.Library()

@register.filter(name='getProcedure')
def getProcedure(E, arg=None) :
    """Return the procedure of the given event."""
    A = E.getPrimaryAlert()
    if A is None : return None

    R = A.reference
    if R : return R.procedure
    else : return ''
