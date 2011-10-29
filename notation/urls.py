from django.conf.urls.defaults import patterns
from notation.views import *


urlpatterns = patterns('',
    (r'^accounts/login/$',  'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page':'/'}),

    (r'^utilisateur/$', utilisateur),
    (r'^bulletin/(?P<object_id>\d+)/$', bulletin),
    (r'^ensemble/(?P<object_id>\d+)/$', ensemble),
    (r'^tuteur/$', index_tuteur),
    (r'^$', index)
)
