from django.conf.urls.defaults import patterns
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.create_update import update_object, create_object
from django.contrib.auth.models import User
from notation.views import *
from notation.models import Entreprise, ProfilUtilisateur, Bulletin

liste_entreprises_dict = {'queryset' : Entreprise.objects.all()}

liste_bulletins_dict = {'queryset' : Bulletin.objects.all()}

liste_eleves_dict = {'queryset' : User.objects.filter(profilutilisateur__user_type='e').order_by('last_name'),
                     'template_name' : 'notation/eleve_list.html'}

liste_tuteurs_dict = {'queryset' : User.objects.filter(profilutilisateur__user_type='t').order_by('last_name'),
                      'template_name' : 'notation/tuteur_list.html'}

liste_formateurs_dict = {'queryset' : User.objects.filter(profilutilisateur__user_type='f').order_by('last_name'),
                        'template_name' : 'notation/formateur_list.html'}

urlpatterns = patterns('',
    (r'^accounts/login/$',  'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page':'/'}),

    (r'^utilisateur/motdepasse/$', motdepasse),
                       
    (r'^bulletins/$', object_list, liste_bulletins_dict, 'liste_bulletin'),
    (r'^bulletins/(?P<blt_id>\d+)/$', bulletin, None, 'bulletin'),
    (r'^bulletins/(?P<blt_id>\d+)/annees/(?P<annee>\d+)/$', annee_bulletin),
    (r'^bulletins/(?P<blt_id>\d+)/annees/(?P<annee>\d+)/groupes/(?P<ens_id>\d+)/$', ensemble_bulletin),

    (r'^entreprises/$', object_list, liste_entreprises_dict, 'liste_entreprise'),
    (r'^entreprises/ajouter/$', detail_entreprise, None, 'ajouter_entreprise'),
    (r'^entreprises/(?P<object_id>\d+)/$', detail_entreprise, None, 'detail_entreprise'),

    (r'^eleves/$', object_list, liste_eleves_dict, 'liste_eleve'),
    (r'^eleves/ajouter/$', ajouter_eleve, None, 'ajouter_eleve'),
    (r'^eleves/(?P<object_id>\d+)/$', modifier_eleve, None, 'detail_eleve'),

    (r'^tuteurs/$', object_list, liste_tuteurs_dict, 'liste_tuteur'),
    (r'^tuteurs/ajouter/$', ajouter_tuteur, None, 'ajouter_tuteur'),
    (r'^tuteurs/(?P<object_id>\d+)/$', detail_tuteur, None, 'detail_tuteur'),

    (r'^formateurs/$', object_list, liste_formateurs_dict, 'liste_formateur'),
    (r'^formateurs/ajouter/$', ajouter_formateur, None, 'ajouter_formateur'),
    (r'^formateurs/(?P<object_id>\d+)/$', detail_formateur, None, 'detail_formateur'),

    (r'^administratif/$', index_admin),
    (r'^formateur/$', index_formateur),
    (r'^tuteur/$', index_tuteur),
    (r'^eleve/$', index_eleve),
    (r'^recherche/$', recherche),
    (r'^$', index)
)
