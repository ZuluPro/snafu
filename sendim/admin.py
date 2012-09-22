from django.contrib import admin
from sendim.models import *


class AlertAdmin(admin.ModelAdmin) :
	list_display = ('date', 'host','service','status','event' )
	list_filter = ( 'status', )
	search_fields = ('service__service', 'host__host')

class EventAdmin(admin.ModelAdmin) :
	list_display = ('date','element','message' )
	search_fields = ('element__host', 'glpi','message' )

class MailSubjectAdmin(admin.ModelAdmin) :
	list_display = ('pk','subject','choiced' )
	search_fields = ('subject', )
	list_filter = ( 'choiced', )

class MailBodyAdmin(admin.ModelAdmin) :
	list_display = ('pk','choiced' )
	search_fields = ('body', )
	list_filter = ( 'choiced', )

admin.site.register(Event, EventAdmin)
admin.site.register(Alert, AlertAdmin)
