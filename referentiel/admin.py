from django.contrib import admin
from referentiel.models import *

class HostAdmin(admin.ModelAdmin):
    list_display = ('name','glpi_id', 'host_type')
    search_fields = ('name','host_type')
    list_filter = ('host_type',)
    list_editable = ('glpi_id', )

class TranslationAdmin(admin.ModelAdmin):
    list_display = ('service','translation')
    search_fields = ('service','translation')
    list_editable = ('translation',)

class ReferenceAdmin(admin.ModelAdmin):
    list_display = ('service','host','mail_type','mail_group','status','mail_criticity','procedure','glpi_category', 'glpi_dst_group', 'glpi_supplier' )
    search_fields = ('host__name', 'service__name')
    list_editable = ('host','mail_type','status','mail_criticity', 'procedure', 'glpi_category', 'glpi_dst_group', 'glpi_supplier')
 
class GlpiSupplierAdmin(admin.ModelAdmin) :
    list_display = ( 'name', 'glpi_id' )
    list_editable = ('glpi_id', )

class MailGroupAdmin(admin.ModelAdmin) :
    list_display = ( 'name', 'to', 'cc', 'ccm')
    list_editable = ('to', 'cc', 'ccm' )

class SupervisorAdmin(admin.ModelAdmin) :
    list_display = ('pk', 'name','login','index')
    search_fields = ('supervisor_type', )
    search_fields = ('name', 'index', 'supervisor_type',)

admin.site.register(Host,HostAdmin)
admin.site.register(Service)
admin.site.register(Status)

admin.site.register(MailType)
admin.site.register(MailGroup, MailGroupAdmin)
#admin.site.register(MailCriticity)

admin.site.register(GlpiCategory)
admin.site.register(GlpiUser)
admin.site.register(GlpiGroup)
admin.site.register(GlpiSupplier, GlpiSupplierAdmin)

admin.site.register(Reference , ReferenceAdmin)
admin.site.register(Translation,TranslationAdmin)

admin.site.register(Supervisor, SupervisorAdmin)
