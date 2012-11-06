from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'sendim.views.index'),

    (r'^login$', 'sendim.views.snafu_login'),
    (r'^logout$', 'sendim.views.snafu_logout'),

    (r'^events$', 'sendim.views.events'),

    (r'^event/agr$', 'sendim.views.eventsAgr'),
    (r"^event/history$", 'sendim.views.eventHistory'),
    (r"^event/reference$", 'sendim.views.eventReference'),
    (r"^event/alerts$", 'sendim.views.eventAlerts'),
    (r"^event/choosePrimaryAlert$", 'sendim.views.choosePrimaryAlert'),
    (r"^event/close$", 'sendim.views.closeEvents'),
    (r"^event/followup$", 'sendim.views.followUp'),

    (r'^event/filter$', 'sendim.views.eventsFiltered'),
    (r'^event/addref$', 'sendim.views.EaddRef'),

    (r'^webservice$', 'sendim.webservice.webservice'),

    (r'^configuration$', 'sendim.views.configuration'),

    (r'^configuration/ref_q$', 'sendim.views.getReferences'),
    (r'^configuration/ref/(?P<ref_id>\d+)/(?P<action>(get|del|add))$', 'sendim.views.reference'),
    (r'^configuration/ref/alert/tabs$', 'sendim.views.getAsWithoutRef'),
    (r'^configuration/ref/alert/(?P<alert_id>\d+)$', 'sendim.views.getAlertWithoutRef'),
    (r'^configuration/ref/alert/(?P<alert_id>\d+)/form$', 'sendim.views.getRefForm'),

    (r'^configuration/hostReference/form$', 'sendim.views.getHostReferenceForm'),
    (r'^configuration/hostReference/(?P<ref_id>\d+)/add$', 'sendim.views.addHostReference'),

    (r'^configuration/trad_q$', 'sendim.views.getTraductions'),
    (r'^configuration/trad/(?P<trad_id>\d+)/(?P<action>(get|del|add))$', 'sendim.views.traduction'),
    (r'^configuration/trad/alert/tabs$', 'sendim.views.getAsWithoutTrad'),
    (r'^configuration/trad/alert/(?P<alert_id>\d+)$', 'sendim.views.getAlertWithoutTrad'),
    (r'^configuration/trad/alert/(?P<alert_id>\d+)/form$', 'sendim.views.getTradForm'),

    (r'^configuration/user/(?P<user_id>\d+)/(?P<action>(get|del|add))$', 'sendim.views.user'),
    (r'^configuration/user_q$', 'sendim.views.getUsers'),
    (r'^configuration/user/form$', 'sendim.views.getUserForm'),

    (r'^configuration/host_q$', 'sendim.views.getHosts'),
    (r'^configuration/host/(?P<host_id>\d+)/(?P<action>(get|del|add))$', 'sendim.views.host'),
    (r'^configuration/host/form$', 'sendim.views.getHostForm'),
    (r'^configuration/host/diff$', 'sendim.views.hostDiff'),

    (r'^configuration/category_q$', 'sendim.views.getCategories'),
    (r'^configuration/category/(?P<cat_id>\d+)/(?P<action>(get|del|add))$', 'sendim.views.category'),
    (r'^configuration/category/form$', 'sendim.views.getGlpiCategoryForm'),
    #(r'^configuration/category/diff$', 'sendim.views.categoryDiff'),

    (r'^configuration/template_q$', 'sendim.views.getMailTemplates'),
    (r'^configuration/template/(?P<temp_id>\d+)/(?P<action>(get|del|add))$', 'sendim.views.mailTemplate'),
    (r'^configuration/template/form$', 'sendim.views.getMailTemplateForm'),

    (r'^configuration/mailGroup_q$', 'sendim.views.getMailGroups'),
    (r'^configuration/mailGroup/(?P<mgroup_id>\d+)/(?P<action>(get|del|add))$', 'sendim.views.mailGroup'),
    (r'^configuration/mailGroup/form$', 'sendim.views.getMailGroupForm'),

    (r'^configuration/mailType_q$', 'sendim.views.getMailTypes'),
    (r'^configuration/mailType/(?P<mtype_id>\d+)/(?P<action>(get|del|add))$', 'sendim.views.mailType'),
    (r'^configuration/mailType/form$', 'sendim.views.getMailTypeForm'),

    (r'^configuration/(?P<action>\w+)/(?P<model>\w+)$', 'sendim.views.confManager'),
    (r'^configuration/(?P<action>\w+)/(?P<model>\w+)/(?P<object_id>\d+)$', 'sendim.views.confManager'),
    #(r'^configuration/mailType/(?P<mtype_id>\d+)/(?P<action>(get|del|add))$', 'sendim.views.mailType'),
    #(r'^configuration/mailType/form$', 'sendim.views.getMailTypeForm'),
)
