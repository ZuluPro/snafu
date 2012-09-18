from sendim.models import *
from referentiel.models import Reference
from django import template

register = template.Library()

@register.filter(name='getProcedure')
def getProcedure(value, arg=None) :
    try:
		A = Alert.objects.order_by('-pk').filter(event__pk__exact=value).exclude(status__status__exact='OK')[0]
                R = Reference.objects.filter(host=A.host, service=A.service, status=A.status)[0]
		return R.procedure
    except : pass
