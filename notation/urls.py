from django.conf.urls.defaults import patterns
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.create_update import update_object, create_object
from django.contrib.auth.models import User
from notation.views import *
from notation.models import Entreprise, ProfilUtilisateur
from notation.forms import EntrepriseForm

liste_entreprises_dict = {'queryset' : Entreprise.objects.all()}
edition_entreprise_dict = {'form_class' : EntrepriseForm,
                           'login_required' : True,
                           'post_save_redirect' : '/entreprises/'}

liste_eleves_dict = {'queryset' : User.objects.filter(profilutilisateur__user_type='e'),
                     'template_name' : 'notation/eleve_list.html'}
edition_eleve_dict = {'model' : User,
                      'login_required' : True,
                      'template_name' : 'notation/eleve_form.html',
                      'post_save_redirect' : '/entreprises/'}

liste_tuteurs_dict = {'queryset' : User.objects.filter(profilutilisateur__user_type='t'),
                      'template_name' : 'notation/tuteur_list.html'}

liste_formateurs_dict = {'queryset' : User.objects.filter(profilutilisateur__user_type='f'),
                        'template_name' : 'notation/formateur_list.html'}

urlpatterns = patterns('',
    (r'^accounts/login/$',  'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page':'/'}),

    (r'^utilisateur/$', utilisateur),
    (r'^bulletin/(?P<object_id>\d+)/$', bulletin),
    (r'^ensemble/(?P<object_id>\d+)/$', ensemble),
                       
    (r'^entreprises/$', object_list, liste_entreprises_dict, 'liste_entreprise'),
    (r'^entreprises/ajouter/$', create_object, edition_entreprise_dict, 'ajouter_entreprise'),
    (r'^entreprises/(?P<object_id>\d+)/$', update_object, edition_entreprise_dict, 'detail_entreprise'),

    (r'^eleves/$', object_list, liste_eleves_dict, 'liste_eleve'),
    (r'^eleves/ajouter/$', ajouter_eleve, None, 'ajouter_eleve'),
    (r'^eleves/(?P<object_id>\d+)/$', update_object, edition_eleve_dict, 'detail_eleve'),

    (r'^tuteurs/$', object_list, liste_tuteurs_dict, 'liste_tuteur'),

    (r'^formateurs/$', object_list, liste_formateurs_dict, 'liste_formateur'),

    (r'^administratif/$', index_admin),
    (r'^formateur/$', index_formateur),
    (r'^tuteur/$', index_tuteur),
    (r'^eleve/$', index_eleve),
    (r'^$', index)
)
