from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'sendim.views.index'),
    (r'^events$', 'sendim.views.events'),

    (r'^event/agr$', 'sendim.views.eventsAgr'),
    (r"^event/history$", 'sendim.views.eventHistory'),
    (r"^event/reference$", 'sendim.views.eventReference'),
    (r"^event/alerts$", 'sendim.views.eventAlerts'),
    (r"^event/choosePrimaryAlert$", 'sendim.views.choosePrimaryAlert'),
    (r"^event/close$", 'sendim.views.closeEvents'),
    (r"^event/followup$", 'sendim.views.followUp'),

    (r'^event/filter$', 'sendim.views.eventsFiltered'),

    (r'^webservice$', 'sendim.webservice.webservice'),

    (r'^configuration$', 'sendim.views.configuration'),
    (r'^configuration/ref_q$', 'sendim.views.getReferences'),
    (r'^configuration/ref/(?P<ref_id>\d+)/(?P<action>(get|del))$', 'sendim.views.reference'),
    (r'^configuration/ref/alert/(?P<alert_id>\d+)$', 'sendim.views.getAlertWithoutRef'),
    (r'^configuration/ref/alert/(?P<alert_id>\d+)/form$', 'sendim.views.getRefForm'),
)
