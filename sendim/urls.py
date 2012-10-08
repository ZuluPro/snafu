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

    (r'^event/filter$', 'sendim.views.eventsFiltered'),

    (r'^webservice$', 'sendim.webservice.webservice'),

    (r'^configuration$', 'sendim.views.configuration'),
)
