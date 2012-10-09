from django.contrib import admin
from sendim.models import *


class AlertAdmin(admin.ModelAdmin) :
	list_display = ('pk','date','host','service','status','event' )
	list_filter = ( 'status','isPrimary' )
	search_fields = ('id', 'service__service', 'host__host')

class EventAdmin(admin.ModelAdmin) :
	list_display = ('pk', 'date','element','message' )
	list_filter = ( 'closed','mail' )
	search_fields = ('id', 'element__host', 'glpi','message' )

class MailTemplateAdmin(admin.ModelAdmin) :
	list_display = ('pk','subject','choosen' )
	search_fields = ('subject','body' )
	list_filter = ( 'choosen', )

admin.site.register(Event, EventAdmin)
admin.site.register(Alert, AlertAdmin)
admin.site.register(MailTemplate, MailTemplateAdmin)
