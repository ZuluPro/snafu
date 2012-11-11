from django.contrib import admin
from sendim.models import *


class AlertAdmin(admin.ModelAdmin) :
    list_display = ('pk','date','host','service','status','event' )
    list_filter = ( 'status','isPrimary' )
    search_fields = ('id', 'service__name', 'host__name')

class EventAdmin(admin.ModelAdmin) :
    list_display = ('pk', 'date','element','message' )
    list_filter = ( 'closed','mail' )
    search_fields = ('id', 'element__name', 'glpi','message' )

class MailTemplateAdmin(admin.ModelAdmin) :
    list_display = ('pk','subject','chosen' )
    search_fields = ('subject','body' )
    list_filter = ( 'chosen', )

class SupervisorAdmin(admin.ModelAdmin) :
    list_display = ('pk', 'name','login','index' )
    search_fields = ('supervisor_type', )
    search_fields = ('name', 'index', 'supervisor_type',)

admin.site.register(Event, EventAdmin)
admin.site.register(Alert, AlertAdmin)
admin.site.register(MailTemplate, MailTemplateAdmin)
admin.site.register(Supervisor, SupervisorAdmin)
