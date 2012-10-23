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
    help = u'Copie d\'une grille de notation et des objets associés'
    args = "id_grille_origine promotion_nouvelle_grille"

    def handle(self, *args, **options):
        if len(args) < 2:
            print u'Mauvais paramètres'
            return
        
        id_grille = int(args[0])
        promotion = int(args[1])

        grille = GrilleNotation.objects.get(id=id_grille)        
        ensembles = EnsembleCapacite.objects.filter(grille=grille)
        savoirs = SavoirEtre.objects.filter(grille=grille)
        
        ngrille = copy(grille)
        ngrille.id = None
        ngrille.promotion = promotion
        ngrille.save()

        for sv in savoirs:
            nsv = copy(sv)
            nsv.id = None
            nsv.grille = ngrille
            nsv.save()
            
        for ens in ensembles:
            capacites = Capacite.objects.filter(ensemble=ens)
            nens = copy(ens)
            nens.id = None
            nens.grille = ngrille
            nens.save()

            for cap in capacites:
                ncap = copy(cap)
                ncap.id = None
                ncap.ensemble = nens
                ncap.save()
                
        print u'Copie de la grille %s pour l\'année %d' % (grille, promotion)
