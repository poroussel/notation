from django.conf.urls.defaults import patterns
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.create_update import update_object, create_object
from django.contrib.auth.models import User
from notation.views import *
from notation.models import Entreprise, ProfilUtilisateur
from notation.forms import EntrepriseForm, UtilisateurForm

liste_entreprises_dict = {'queryset' : Entreprise.objects.all()}
edition_entreprise_dict = {'form_class' : EntrepriseForm,
                           'login_required' : True,
                           'post_save_redirect' : '/entreprises/'}

liste_eleves_dict = {'queryset' : User.objects.filter(profilutilisateur__user_type='e').order_by('last_name'),
                     'template_name' : 'notation/eleve_list.html'}

liste_tuteurs_dict = {'queryset' : User.objects.filter(profilutilisateur__user_type='t').order_by('last_name'),
                      'template_name' : 'notation/tuteur_list.html'}
edition_tuteur_dict = {'form_class' : UtilisateurForm,
                       'login_required' : True,
                       'template_name' : 'notation/tuteur_form.html',
                       'post_save_redirect' : '/tuteurs/'}

liste_formateurs_dict = {'queryset' : User.objects.filter(profilutilisateur__user_type='f').order_by('last_name'),
                        'template_name' : 'notation/formateur_list.html'}
edition_formateur_dict = {'form_class' : UtilisateurForm,
                          'login_required' : True,
                          'template_name' : 'notation/formateur_form.html',
                          'post_save_redirect' : '/formateurs/'}

urlpatterns = patterns('',
    (r'^accounts/login/$',  'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page':'/'}),

    (r'^utilisateur/$', utilisateur),
    (r'^bulletins/(?P<blt_id>\d+)/$', bulletin),
    (r'^bulletins/(?P<blt_id>\d+)/annees/(?P<annee>\d+)/$', annee_bulletin),
    (r'^bulletins/(?P<blt_id>\d+)/annees/(?P<annee>\d+)/groupes/(?P<ens_id>\d+)/$', ensemble_bulletin),

    (r'^entreprises/$', object_list, liste_entreprises_dict, 'liste_entreprise'),
    (r'^entreprises/ajouter/$', create_object, edition_entreprise_dict, 'ajouter_entreprise'),
    (r'^entreprises/(?P<object_id>\d+)/$', update_object, edition_entreprise_dict, 'detail_entreprise'),

    (r'^eleves/$', object_list, liste_eleves_dict, 'liste_eleve'),
    (r'^eleves/ajouter/$', ajouter_eleve, None, 'ajouter_eleve'),
    (r'^eleves/(?P<object_id>\d+)/$', modifier_eleve, None, 'detail_eleve'),

    (r'^tuteurs/$', object_list, liste_tuteurs_dict, 'liste_tuteur'),
    (r'^tuteurs/ajouter/$', ajouter_tuteur, None, 'ajouter_tuteur'),
    (r'^tuteurs/(?P<object_id>\d+)/$', update_object, edition_tuteur_dict, 'detail_tuteur'),

    (r'^formateurs/$', object_list, liste_formateurs_dict, 'liste_formateur'),
    (r'^formateurs/ajouter/$', ajouter_formateur, None, 'ajouter_formateur'),
    (r'^formateurs/(?P<object_id>\d+)/$', update_object, edition_formateur_dict, 'detail_formateur'),

    (r'^administratif/$', index_admin),
    (r'^formateur/$', index_formateur),
    (r'^tuteur/$', index_tuteur),
    (r'^eleve/$', index_eleve),
    (r'^$', index)
)
