# -*- coding: utf-8 -*-

from copy import copy
from optparse import make_option
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from cfai.notation.models import *

# FIXME : modifier pour uniquement copier le contenu d'une grille existante
# vers une autre grille existante (créée dans l'admin)
class Command(BaseCommand):
    help = u'Copie d\'une grille de notation et des objets associés vers une autre grille, cette dernière étant nettoyée automatiquement.'
    args = "id_grille_origine id_grille_destination"

    def handle(self, *args, **options):
        if len(args) < 2:
            print u'Mauvais paramètres'
            return
        
        id_grille = int(args[0])
        id_desti = int(args[1])

        grille = GrilleNotation.objects.get(id=id_grille)
        ngrille = GrilleNotation.objects.get(id=id_desti)

        # Nettoyage des objets liées à la grille de destination
        # Les capacites et savoirs être sont supprimés en cascade
        SavoirEtre.objects.filter(grille=ngrille).delete()
        Theme.objects.filter(grille=ngrille).delete()
        EnsembleCapacite.objects.filter(grille=ngrille).delete()

        themes = Theme.objects.filter(grille=grille)
        savoirs = SavoirEtre.objects.filter(grille=grille)

        for sv in savoirs:
            nsv = copy(sv)
            nsv.id = None
            nsv.grille = ngrille
            nsv.save()

        for th in themes:
            ensembles = EnsembleCapacite.objects.filter(theme=th)
            nth = copy(th)
            nth.id = None
            nth.grille = ngrille
            nth.save()
            
            for ens in ensembles:
                capacites = Capacite.objects.filter(ensemble=ens)
                nens = copy(ens)
                nens.id = None
                nens.grille = ngrille
                nens.theme = nth
                nens.save()

                for cap in capacites:
                    ncap = copy(cap)
                    ncap.id = None
                    ncap.ensemble = nens
                    ncap.save()
                
        print u'Copie de la grille %s vers la grille %s' % (grille, ngrille)
