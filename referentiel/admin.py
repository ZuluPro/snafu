from django.contrib import admin
from referentiel.models import *

class HostAdmin(admin.ModelAdmin):
    list_display = ('host','glpi_id', 'host_type')
    search_fields = ('host','host_type')
    list_filter = ('host_type',)
    list_editable = ('glpi_id', )

class TraductionAdmin(admin.ModelAdmin):
    list_display = ('service','traduction')
    search_fields = ('service','traduction')
    list_editable = ('traduction',)

class ReferenceAdmin(admin.ModelAdmin):
    list_display = ('service','host','mail_type','mail_group','status','mail_criticity','procedure','glpi_category', 'glpi_dst_group', 'glpi_supplier' )
    search_fields = ('host__host', 'service__service')
    list_editable = ('host','mail_type','mail_group','status','mail_criticity', 'procedure', 'glpi_category', 'glpi_dst_group', 'glpi_supplier')
 
class GlpiSupplierAdmin(admin.ModelAdmin) :
    list_display = ( 'glpi_supplier', 'glpi_id' )
    list_editable = ('glpi_id', )

class MailGroupAdmin(admin.ModelAdmin) :
    list_display = ( 'mail_group', 'to', 'cc', 'ccm' )
    list_editable = ('to', 'cc', 'ccm' )

admin.site.register(Host,HostAdmin)
admin.site.register(Service)
admin.site.register(Status)

admin.site.register(MailType)
admin.site.register(MailGroup, MailGroupAdmin)
admin.site.register(MailCriticity)

admin.site.register(GlpiUrgency)
admin.site.register(GlpiPriority)
admin.site.register(GlpiCategory)
admin.site.register(GlpiUser)
admin.site.register(GlpiGroup)
admin.site.register(GlpiSupplier, GlpiSupplierAdmin)
admin.site.register(GlpiImpact)

admin.site.register(Reference , ReferenceAdmin)
admin.site.register(Traduction,TraductionAdmin)
