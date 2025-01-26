from django.conf.urls.defaults import patterns
from django.views.generic.list_detail import object_list
from django.contrib.auth.models import User
from cfai.notation.views import *
from cfai.notation.models import Entreprise, ProfilUtilisateur


liste_tuteurs_dict = {
    'queryset' : User.objects.filter(profilutilisateur__user_type='t').filter(profilutilisateur__suppression=None).order_by('last_name'),
    'template_name' : 'notation/tuteur_list.html'
    }

liste_formateurs_dict = {
    'queryset' : User.objects.filter(profilutilisateur__user_type__in=['f', 'F']).filter(profilutilisateur__suppression=None).order_by('last_name'),
    'template_name' : 'notation/formateur_list.html'
    }

liste_pilotes_dict = {
    'queryset' : User.objects.filter(profilutilisateur__user_type__in=['p', 'F']).filter(profilutilisateur__suppression=None).order_by('last_name'),
    'template_name' : 'notation/pilote_list.html'
    }

urlpatterns = patterns('',
    (r'^accounts/login/$',  'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page':'/'}),

    (r'^utilisateur/motdepasse/$', motdepasse),
    (r'^utilisateur/profil/$', profil),

    (r'^suppression/(?P<model>[a-zA-Z]+)/(?P<object_id>\d+)/$', suppression_objet),

    (r'^bulletins/$', liste_bulletin, None, 'liste_bulletin'),
    (r'^bulletins/(?P<blt_id>\d+)/$', bulletin, None, 'bulletin'),
    (r'^bulletins/(?P<blt_id>\d+)/annees/(?P<annee>\d+)/$', annee_bulletin),
    (r'^bulletins/(?P<blt_id>\d+)/annees/(?P<annee>\d+)/groupes/(?P<ens_id>\d+)/$', ensemble_bulletin),

    (r'^grilles/(?P<object_id>\d+)/annee/(?P<annee>\d+)/$', resume_grille, None, 'resume_grille'),

    (r'^entreprises/$', liste_entreprise, None, 'liste_entreprise'),
    (r'^entreprises/ajouter/$', detail_entreprise, None, 'ajouter_entreprise'),
    (r'^entreprises/(?P<object_id>\d+)/$', detail_entreprise, None, 'detail_entreprise'),

    (r'^eleves/$', liste_eleve, None, 'liste_eleve'),
    (r'^eleves/supprimes/$', liste_eleve_supprime, None, 'liste_eleve_supprime'),
    (r'^eleves/ajouter/$', ajouter_eleve, None, 'ajouter_eleve'),
    (r'^eleves/(?P<object_id>\d+)/$', modifier_eleve, None, 'detail_eleve'),

    (r'^tuteurs/$', object_list, liste_tuteurs_dict, 'liste_tuteur'),
    (r'^tuteurs/ajouter/$', ajouter_tuteur, None, 'ajouter_tuteur'),
    (r'^tuteurs/(?P<object_id>\d+)/$', detail_tuteur, None, 'detail_tuteur'),

    (r'^formateurs/$', object_list, liste_formateurs_dict, 'liste_formateur'),
    (r'^formateurs/ajouter/$', ajouter_formateur, None, 'ajouter_formateur'),
    (r'^formateurs/(?P<object_id>\d+)/$', detail_formateur, None, 'detail_formateur'),

    (r'^pilotes/$', object_list, liste_pilotes_dict, 'liste_pilote'),
    (r'^pilotes/ajouter/$', ajouter_pilote, None, 'ajouter_pilote'),
    (r'^pilotes/(?P<object_id>\d+)/$', detail_pilote, None, 'detail_pilote'),

    (r'^formations/$', liste_formation, None, 'liste_formation'),

    (r'^administratif/$', index_admin),
    (r'^gestion/$', index_gestion, None, 'index_gestion'),
    (r'^assistance/$', index_assistance, None, 'index_assistance'),
    (r'^formateur/$', index_formateur),
    (r'^tuteur/$', index_tuteur),
    (r'^eleve/$', index_eleve),
    (r'^recherche/$', recherche),
    (r'^$', index)
)
