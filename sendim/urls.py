from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'sendim.views.index'),

    (r'^login$', 'sendim.views.snafu_login'),
    (r'^logout$', 'sendim.views.snafu_logout'),
    (r'^apropos$', 'sendim.views.apropos'),

    (r'^events$', 'sendim.views.events'),

    (r'^event/agr$', 'sendim.views.eventsAgr'),
    (r"^event/history$", 'sendim.views.eventHistory'),
    (r"^event/reference$", 'sendim.views.eventReference'),
    (r"^event/alerts$", 'sendim.views.eventAlerts'),
    (r"^event/choosePrimaryAlert$", 'sendim.views.choosePrimaryAlert'),
    (r"^event/close$", 'sendim.views.closeEvents'),
    (r"^event/followup$", 'sendim.views.followUp'),
    (r"^event/reloadAlerts$", 'sendim.views.reload_alerts'),

    (r'^event/filter$', 'sendim.views.eventsFiltered'),
    (r'^event/addref$', 'sendim.views.EaddRef'),

    (r'^webservice$', 'sendim.webservice.webservice'),

    (r'^configuration$', 'sendim.views.configuration'),

    (r'^configuration/ref/form/(?P<_type>(simple|host|big))$', 'sendim.views.getRefForm'),
    (r'^configuration/ref/add$', 'sendim.views.addReference'),

    (r'^configuration/ref_q$', 'sendim.views.getReferences'),

#    (r'^configuration/host/diff$', 'sendim.views.hostDiff'),

    (r'^configuration/update/?$', 'sendim.views.update'),
    (r'^configuration/(?P<action>\w+)/(?P<model>\w+)/?$', 'sendim.views.confManager'),
    (r'^configuration/(?P<action>\w+)/(?P<model>\w+)/(?P<object_id>\d+)/?$', 'sendim.views.confManager'),
)
