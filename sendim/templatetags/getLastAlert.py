from sendim.models import *
from django import template

register = template.Library()

@register.filter(name='getLastAlert')
def getLastAlert(value, arg=None) :
	try :
		A = Alert.objects.order_by('-pk').filter(event__pk__exact=value).exclude(status__status__exact='OK')[0]
		return A.pk
	except : return ""
