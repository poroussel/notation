from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from django.views.static import serve

admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    (r'^', include('cfai.notation.urls')),               
)

if settings.SERVE_STATIC == True:
    urlpatterns += patterns('',
       (r'^static/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}))
