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

    # Largeur des colonnes
    sheet.col(1).width = 15000
    sheet.col(5).width += 400
    sheet.col(6).width = 7000
    
    # Entête globale
    lig = 0
    gras = easyxf('font: name Arial, bold on; pattern: pattern solid, fore-colour bright_green; borders: left medium, top medium, right medium')
    sheet.write_merge(lig, lig, 1, 4, u'Diplôme d\'ingénieur ENSMM Intitulé : ', gras)
    lig += 1
    gras = easyxf('font: name Arial, bold on; pattern: pattern solid, fore-colour bright_green; borders: left medium, right medium')
    sheet.write_merge(lig, lig, 1, 4, u'Filière ITII, Organisme coordinateur CFAI Sud Franche-Comté; Branche Professionnelle UIMM', gras)
    lig += 1

    gros = easyxf('font: name Arial, bold on, height 240; borders: left medium, right medium')
    normal = easyxf('font: name Arial, bold on, height 180; borders: left medium, right medium')
    sheet.write_merge(lig, lig, 1, 4, u'Apprenti : ', gros)
    sheet.row(lig).height = sheet.row(lig).height * 3 / 2
    lig += 1
    sheet.write_merge(lig, lig, 1, 4, u'Année de formation : ', normal)
    lig += 1
    sheet.write_merge(lig, lig, 1, 4, u'N° de tél portable : Adresse email : ', normal)
    lig += 1
    
    sheet.write_merge(lig, lig, 1, 4, u'Entreprise : ', gros)
    sheet.row(lig).height = sheet.row(lig).height * 3 / 2
    lig += 1
    sheet.write_merge(lig, lig, 1, 4, u'Adresse : ', normal)
    lig += 1
    
    sheet.write_merge(lig, lig, 1, 4, u'Tuteur : ', gros)
    sheet.row(lig).height = sheet.row(lig).height * 3 / 2
    lig += 1
    sheet.write_merge(lig, lig, 1, 4, u'N° de tél portable : Adresse email : ', normal)
    lig += 1
    normal = easyxf('font: name Arial, bold on, height 180; borders: left medium, right medium, bottom medium')
    sheet.write_merge(lig, lig, 1, 4, u'Chargé de promotion : ', normal)
    
    titre = easyxf('font: name Arial, color-index black, bold on, height 160; borders: left medium, top medium, right medium, bottom medium; align: horiz centre')
    lig = 13
    sheet.write(lig, 2, u'1ère année', titre)
    sheet.write(lig, 3, u'2ème année', titre)
    sheet.write(lig, 4, u'3ème année', titre)
    sheet.write(lig, 5, u'Cours associé', titre)
    sheet.write(lig, 6, u'Actions réalisées ou initiées', titre)

    titre = easyxf('font: name Arial, bold on, height 160; borders: left medium, top medium, right medium, bottom medium; align: vert centre, horiz centre; pattern: pattern solid, fore-colour grey25')
    titreg = easyxf('font: name Arial, bold on, height 160; borders: left medium, top medium, right medium, bottom medium; align: vert centre; pattern: pattern solid, fore-colour grey25')
    normal = easyxf('font: name Arial, height 160; borders: left medium, top medium, right medium, bottom medium; align: vert centre')
    centre = easyxf('font: name Arial, height 160; borders: left medium, top medium, right medium, bottom medium; align: vert centre, horiz centre')
    
    centrer = easyxf('font: name Arial, height 160; borders: left medium, top medium, right medium, bottom medium; align: vert centre, horiz centre; pattern: pattern solid, fore-colour red')
    centrev = easyxf('font: name Arial, height 160; borders: left medium, top medium, right medium, bottom medium; align: vert centre, horiz centre; pattern: pattern solid, fore-colour green')
    centreb = easyxf('font: name Arial, height 160; borders: left medium, top medium, right medium, bottom medium; align: vert centre, horiz centre; pattern: pattern solid, fore-colour blue')
    
    lig += 1
    ensembles = EnsembleCapacite.objects.filter(grille = blt.grille)
    for ens in ensembles:
        capacites = Capacite.objects.filter(ensemble = ens).order_by('numero')
        if capacites.count() == 0:
            continue
        
        sheet.write(lig, 0, ens.partie)
        sheet.write_merge(lig, lig, 1, 6, u'%d %s' % (ens.numero, ens.libelle), titreg)
        lig += 1

        for cap in capacites:
            # Création des cellules même vides pour la bordure
            sheet.write(lig, 1, u'%d.%d %s' % (ens.numero, cap.numero, cap.libelle), normal)
            
            notes = Note.objects.filter(bulletin=blt, capacite=cap)
            n = notes.filter(annee=0)
            sheet.write(lig, 2, n and n[0].valeur or '', cap.an_1 and centrer or centre)
            n = notes.filter(annee=1)
            sheet.write(lig, 3, n and n[0].valeur or '', cap.an_2 and centrev or centre)
            n = notes.filter(annee=1)
            sheet.write(lig, 4, n and n[0].valeur or '', cap.an_3 and centreb or centre)
            sheet.write(lig, 5, cap.cours, centre)
            sheet.write(lig, 6, '', centre)

            lig = lig + 1
            
        sheet.write(lig, 1, u'Note sur 5')
        lig = lig + 2
        
    book.save(response)
    return response
