from sendim.models import *
from django import template

register = template.Library()

@register.filter(name='getEventColor')
def getEventColor(value, arg=None) :
    E = value
    A = E.getPrimaryAlert()
    As = E.getAlerts().filter(host=A.host,service=A.service).exclude(pk=A.pk).order_by('-date')

    if not As : return A.status.status.lower()+'-status'
    elif As[0].status.status == 'OK' : return ''
    else : return As[0].status.status.lower()+'-status'
