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

    (r'^configuration/host/diff$', 'sendim.views.hostDiff'),

    (r'^configuration/(?P<action>\w+)/(?P<model>\w+)$', 'sendim.views.confManager'),
    (r'^configuration/(?P<action>\w+)/(?P<model>\w+)/(?P<object_id>\d+)$', 'sendim.views.confManager'),
    #(r'^configuration/mailType/(?P<mtype_id>\d+)/(?P<action>(get|del|add))$', 'sendim.views.mailType'),
    #(r'^configuration/mailType/form$', 'sendim.views.getMailTypeForm'),
)
