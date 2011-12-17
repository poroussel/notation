# -*- coding: utf-8 -*-

from django.http import HttpResponse
from cfai.notation.models import *
from xlwt import *
import unicodedata

chaine = u"éèêäûôü"
def bulletin_xls(request, blt):
    # Suppression des caractères accentués du nom de l'apprenti
    nom = unicodedata.normalize('NFKD', blt.eleve.get_full_name()).encode('ASCII', 'ignore')
    response = HttpResponse(mimetype='application/xls')
    response['Content-Disposition'] = 'attachment; filename="%s.xls"' % nom

    # Creation d'un workbook en Unicode
    book = Workbook(encoding='cp1251')
    sheet = book.add_sheet('Bulletin %d-%d' % (blt.grille.promotion, blt.grille.promotion + blt.grille.duree))

    # Les entêtes de colonnes sur la deuxième ligne
    sheet.write(2, 0, u'Partie spécifique')
    sheet.write(2, 1, u'Capacités professionnelles et Tâches professionnelles (Etre capable de…)')
    sheet.write(2, 2, u'1ère année')
    sheet.write(2, 3, u'2ème année')
    sheet.write(2, 4, u'3ème année')
    sheet.write(2, 5, u'Cours associé')
    sheet.write(2, 6, u'Résultats - indicateurs de performance - validation (Actions réalisées ou initiées en entreprise)')

    lig = 3
    ensembles = EnsembleCapacite.objects.filter(grille = blt.grille)
    for ens in ensembles:
        capacites = Capacite.objects.filter(ensemble = ens).order_by('numero')
        if capacites.count() == 0:
            continue
        
        sheet.write(lig, 0, ens.partie)
        sheet.write(lig, 1, u'%d %s' % (ens.numero, ens.libelle))
        lig = lig + 1

        for cap in capacites:
            sheet.write(lig, 1, u'%d.%d %s' % (ens.numero, cap.numero, cap.libelle))
            sheet.write(lig, 5, cap.cours)

            notes = Note.objects.filter(bulletin=blt, capacite=cap)
            for note in notes:
                sheet.write(lig, 2 + note.annee, note.valeur)
                
            lig = lig + 1
            
        sheet.write(lig, 1, u'Note sur 5')
        lig = lig + 1
        
    book.save(response)
    return response
