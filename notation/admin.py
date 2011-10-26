from django.contrib import admin
from notation.models import *

admin.site.register(Eleve)
admin.site.register(Entreprise)
admin.site.register(Competence)
admin.site.register(CommentaireCompetence)
admin.site.register(Note)
admin.site.register(EnsembleCompetence)
admin.site.register(GrilleNotation)

