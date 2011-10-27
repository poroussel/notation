from django.contrib import admin
from notation.models import *

admin.site.register(Eleve)
admin.site.register(Entreprise)
admin.site.register(Capacite)
admin.site.register(Commentaire)
admin.site.register(Note)
admin.site.register(GrilleNotation)

class EnsembleCapaciteAdmin(admin.ModelAdmin):
    list_filter = ('grille', 'partie',)
admin.site.register(EnsembleCapacite, EnsembleCapaciteAdmin)
