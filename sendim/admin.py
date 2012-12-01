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

class CommandAdmin(admin.ModelAdmin) :
    list_display = ('name','string') 
    search_fields = ('name','string') 

class CommandLogAdmin(admin.ModelAdmin) :
    list_display = ('date','command','status') 
    search_fields = ('command__name','stdin','stdout','stderr') 
    list_filter = ('status',)

admin.site.register(Event, EventAdmin)
admin.site.register(Alert, AlertAdmin)
admin.site.register(MailTemplate, MailTemplateAdmin)
admin.site.register(Command, CommandAdmin)
admin.site.register(CommandLog, CommandLogAdmin)
