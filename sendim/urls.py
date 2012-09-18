from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^s$', 'sendim.views.events'),
    (r'^s/(?P<page>\d*)$', 'sendim.views.events'),

    (r'^sAgr$', 'sendim.views.eventsAgr'),
    (r"^History$", 'sendim.views.eventHistory'),
    (r"^Reference$", 'sendim.views.eventReference'),
    (r"^Alerts$", 'sendim.views.eventAlerts'),

    (r'^s/filter$', 'sendim.views.eventsFiltered'),
    (r'^mail$', 'sendim.views.createMail'),

    (r'^alerts$', 'sendim.views.alerts'),
    (r'^alerts/(?P<page>\d*)$', 'sendim.views.alerts'),
)
