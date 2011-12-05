from django.contrib import admin
from cfai.notation.models import *

admin.site.register(ProfilUtilisateur)
admin.site.register(Bulletin)
admin.site.register(Entreprise)
admin.site.register(GrilleNotation)
admin.site.register(Formation)
admin.site.register(Moyenne)

class EnsembleCapaciteAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'grille')
    list_filter = ('partie',)
    search_fields = ['grille__formation', 'libelle']
admin.site.register(EnsembleCapacite, EnsembleCapaciteAdmin)

class CapaciteAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'cours', 'an_1', 'an_2', 'an_3')
    list_filter = ('ensemble',)
admin.site.register(Capacite, CapaciteAdmin)

class SavoirEtreAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'grille')
    list_filter = ('grille',)
    ordering = ['grille']
admin.site.register(SavoirEtre, SavoirEtreAdmin)

class NoteAdmin(admin.ModelAdmin):
    list_display = ('eleve',
                    'sujet',
                    'annee',
                    'valeur',
                    'auteur_modification',
                    'date_modification')
    list_display_links = ('sujet',)
admin.site.register(Note, NoteAdmin)

class CommentaireAdmin(admin.ModelAdmin):
    list_display = ('eleve',
                    'ensemble',
                    'texte',
                    'auteur_modification',
                    'date_modification')
    list_display_links = ('ensemble',)
admin.site.register(Commentaire, CommentaireAdmin)
