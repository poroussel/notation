from django.contrib import admin
from notation.models import *

admin.site.register(ProfilUtilisateur)
admin.site.register(Bulletin)
admin.site.register(Entreprise)
admin.site.register(Commentaire)
admin.site.register(Note)
admin.site.register(GrilleNotation)

class EnsembleCapaciteAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'grille',)
    list_filter = ('partie',)
    search_fields = ['grille__formation', 'libelle']
admin.site.register(EnsembleCapacite, EnsembleCapaciteAdmin)

class CapaciteAdmin(admin.ModelAdmin):
    list_filter = ('ensemble',)
    ordering = ['ensemble']
admin.site.register(Capacite, CapaciteAdmin)
