from django.conf.urls.defaults import patterns
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.create_update import update_object
from notation.views import *
from notation.models import Entreprise
from notation.forms import EntrepriseForm

liste_entreprises_dict = {'queryset' : Entreprise.objects.all()}
edition_entreprise_dict = {'form_class' : EntrepriseForm,
                           'login_required' : True,
                           'post_save_redirect' : '/entreprises/'}

urlpatterns = patterns('',
    (r'^accounts/login/$',  'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page':'/'}),

    (r'^utilisateur/$', utilisateur),
    (r'^bulletin/(?P<object_id>\d+)/$', bulletin),
    (r'^ensemble/(?P<object_id>\d+)/$', ensemble),
                       
    (r'^entreprises/$', object_list, liste_entreprises_dict, 'liste_entreprise'),
    (r'^entreprises/(?P<object_id>\d+)/$', update_object, edition_entreprise_dict, 'detail_entreprise'),
                       
    (r'^administratif/ajouter/eleve/$', ajouter_eleve),
    (r'^administratif/ajouter/tuteur/$', ajouter_tuteur),
    (r'^administratif/ajouter/formateur/$', ajouter_formateur),
    (r'^administratif/$', index_admin),
                       
    (r'^formateur/$', index_formateur),
    (r'^tuteur/$', index_tuteur),
    (r'^eleve/$', index_eleve),
    (r'^$', index)
)
