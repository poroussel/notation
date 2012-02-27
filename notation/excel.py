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

    # Entête globale
    gras = easyxf('font: name Arial, color-index black, bold on; pattern: pattern solid, fore-colour light-green')
    sheet.col(1).width = 15000
    lig = 0
    sheet.write_merge(lig, lig, 1, 4, u'Diplôme d\'ingénieur ENSMM Intitulé : ', gras)
    lig += 1
    sheet.write_merge(lig, lig, 1, 4, u'Filière ITII, Organisme coordinateur CFAI Sud Franche-Comté; Branche Professionnelle UIMM', gras)
    lig += 1

    gros = easyxf('font: name Arial, color-index black, bold on, height 240')
    normal = easyxf('font: name Arial, color-index black, bold on, height 180')
    sheet.write(lig, 1, u'Apprenti : ', gros)
    sheet.row(lig).height = sheet.row(lig).height * 3 / 2
    lig += 1
    sheet.write(lig, 1, u'Année de formation : ', normal)
    lig += 1
    sheet.write(lig, 1, u'N° de tél portable : Adresse email : ', normal)
    lig += 1
    
    sheet.write(lig, 1, u'Entreprise : ', gros)
    sheet.row(lig).height = sheet.row(lig).height * 3 / 2
    lig += 1
    sheet.write(lig, 1, u'Adresse : ', normal)
    lig += 1
    
    sheet.write(lig, 1, u'Tuteur : ', gros)
    sheet.row(lig).height = sheet.row(lig).height * 3 / 2
    lig += 1
    sheet.write(lig, 1, u'N° de tél portable : Adresse email : ', normal)
    lig += 1
    sheet.write(lig, 1, u'Chargé de promotion : ', normal)
    
    lig = 13
    # Les entêtes de colonnes sur la deuxième ligne
    sheet.write(lig, 0, u'Partie spécifique')
    sheet.write(lig, 1, u'Capacités professionnelles et Tâches professionnelles (Etre capable de…)')
    sheet.write(lig, 2, u'1ère année')
    sheet.write(lig, 3, u'2ème année')
    sheet.write(lig, 4, u'3ème année')
    sheet.write(lig, 5, u'Cours associé')
    sheet.write(lig, 6, u'Résultats - indicateurs de performance - validation (Actions réalisées ou initiées en entreprise)')

    lig += 1
    ensembles = EnsembleCapacite.objects.filter(grille = blt.grille)
    for ens in ensembles:
        capacites = Capacite.objects.filter(ensemble = ens).order_by('numero')
        if capacites.count() == 0:
            continue
        
        sheet.write(lig, 0, ens.partie)
        sheet.write(lig, 1, u'%d %s' % (ens.numero, ens.libelle))
        lig += 1

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
