from sendim.models import *
from django import template

register = template.Library()

@register.filter(name='getAlertColor')
def getAlertColor(value, arg=None) :
    try :
        if arg == 'event' : value = Alert.objects.filter(event__pk__exact=value).order_by('-date')[0].status.status
        for color,status in ( ('rgb(80,240,80)','UP'), ('rgb(80,240,80)','OK'), ('rgb(240,80,80)','CRITICAL'), ('rgb(240,80,80)','DOWN'), ('rgb(240,240,80)','WARNING'), ('rgb(240,80,240)','UNKNOWN') ) :
            if ( value=='UP' or value=='OK' ) and arg=='event': continue
            if value == status : 
                return color
    except IndexError: return 'rgb(200,200,200)'
