from django.conf.urls.defaults import patterns
from django.contrib.auth.views import login, logout
from notation.views import *


urlpatterns = patterns('',
    (r'^accounts/login/$',  login),
    (r'^accounts/logout/$', logout, {'next_page':'/'}),

    (r'^bulletin/(?P<object_id>\d+)/$', bulletin),
    (r'^tuteur/$', index_tuteur),
    (r'^$', index)
)
