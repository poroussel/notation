# -*- coding: utf-8 -*-

import json
from datetime import date
from copy import copy
from optparse import make_option
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from django.db import transaction
from cfai.notation.models import *

class Command(BaseCommand):
    help = u"Export d'une grille de notation en json"
    args = "id_grille"

    def handle(self, *args, **options):
        if len(args) < 1:
            print u'Mauvais paramètres'
            return

        id_grille = int(args[0])
        grille = GrilleNotation.objects.get(pk=id_grille)

        doc = {'formation': grille.frm.libelle.encode('utf8')}
        doc['promotion'] = grille.promotion
        doc['duree'] = grille.duree

        doc['themes'] = [{
            'libelle': th.libelle.encode('utf8'),
            'ensembles': [{
                'libelle': ens.libelle.encode('utf8'),
                'capacites': [cap.libelle.encode('utf8') for cap in ens.capacite_set.all()]
                } for ens in th.ensemblecapacite_set.all()]
        } for th in grille.theme_set.all()]

        print u'Génération du ficher grille-{}-{}.json'.format(id_grille, date.today())
        with open('grille-{}-{}.json'.format(id_grille, date.today()), 'wt') as fd:
            json.dump(doc, fd, indent=4, sort_keys=True, ensure_ascii=False)
