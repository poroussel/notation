# -*- coding: utf-8 -*-

import json
from copy import copy
from optparse import make_option
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from django.db import transaction
from cfai.notation.models import *

class Command(BaseCommand):
    help = u"Import d'une grille de notation décrite en json"
    args = "fichier_grille"

    def handle(self, *args, **options):
        if len(args) < 1:
            print u'Mauvais paramètres'
            return

        path = args[0]

        with open(path, 'r') as fd:
            data = json.load(fd)

        formation = Formation.objects.get(libelle=data['formation'])
        promotion = data['promotion']
        duree = data['duree']

        print u'Creation grille pour {} / {} / {}'.format(formation, promotion, duree)

        grilles = GrilleNotation.objects.filter(frm=formation, promotion=promotion, duree=duree)
        if len(grilles) > 0:
            print u'La grille existe déjà, abandon...'
            return

        with transaction.commit_on_success():
            grille = GrilleNotation(frm=formation, promotion=promotion, duree=duree, archive=False)
            grille.save()

            nuens = 1
            for ct, theme in enumerate(data['themes']):
                print u'Theme {}:{}'.format(ct+1, theme['libelle'])
                th = Theme(grille=grille, position=ct+1, libelle=theme['libelle'])
                th.save()

                for ensemble in theme['ensembles']:
                    print u'Ensemble {}:{}'.format(nuens, ensemble['libelle'])
                    ens = EnsembleCapacite(grille=grille, theme=th, numero=nuens, libelle=ensemble['libelle'])
                    ens.save()
                    nuens += 1

                    for cc, capacite in enumerate(ensemble['capacites']):
                        print u'Capacité {}:{}'.format(cc+1, capacite)
                        cap = Capacite(ensemble=ens, numero=cc+1, libelle=capacite)
                        cap.save()

            for cse, setre in enumerate(data['savoirsetre']):
                print u'Savoir être {}:{}'.format(cse, setre)
                se = SavoirEtre(grille=grille, libelle=setre)
                se.save()

        print 'done'
