# -*- coding: utf-8 -*-

from django.http import HttpResponse
from cfai.notation.models import *
from xlwt import *
import unicodedata

def evaluation(value):
    if value:
        return value[0].get_valeur_display()
    return u'Non renseigné'

chaine = u"éèêäûôü"
def bulletin_xls(request, blt):
    # Suppression des caractères accentués du nom de l'apprenti
    nom = unicodedata.normalize('NFKD', blt.eleve.get_full_name()).encode('ASCII', 'ignore')
    response = HttpResponse(mimetype='application/xls')
    response['Content-Disposition'] = 'attachment; filename="%s.xls"' % nom

    # Creation d'un workbook en Unicode
    book = Workbook(encoding='cp1251')
    sheet = book.add_sheet('Bulletin %d-%d' % (blt.grille.promotion, blt.grille.promotion + blt.grille.duree))
    sheet.set_portrait(False)
    
    # Largeur des colonnes
    sheet.col(1).width = 15000
    sheet.col(5).width = 12000
    sheet.col(6).width = 12000
    sheet.col(7).width = 12000
    
    # Entête globale
    lig = 0
    gras = easyxf('font: name Arial, bold on; pattern: pattern solid, fore-colour bright_green; borders: left medium, top medium, right medium')
    sheet.write_merge(lig, lig, 1, 4, u'Diplôme d\'ingénieur ENSMM Intitulé : %s' % (blt.grille.frm), gras)
    lig += 1
    gras = easyxf('font: name Arial, bold on; pattern: pattern solid, fore-colour bright_green; borders: left medium, right medium')
    sheet.write_merge(lig, lig, 1, 4, u'Filière ITII, Organisme coordinateur CFAI Sud Franche-Comté; Branche Professionnelle UIMM', gras)
    lig += 1

    gros = easyxf('font: name Arial, bold on, height 240; borders: left medium, right medium')
    normal = easyxf('font: name Arial, bold on, height 180; borders: left medium, right medium')
    sheet.write_merge(lig, lig, 1, 4, u'Apprenti : %s' % (blt.eleve.get_profile().nom_complet), gros)
    sheet.row(lig).height = sheet.row(lig).height * 3 / 2
    lig += 1
    sheet.write_merge(lig, lig, 1, 4, u'Années de formation : %s / %s' % (blt.grille.promotion, blt.grille.promotion + blt.grille.duree), normal)
    lig += 1
    sheet.write_merge(lig, lig, 1, 4, u'N° de tél portable %s : Adresse email : %s' % (blt.eleve.get_profile().phone_number, blt.eleve.email), normal)
    lig += 1
    
    sheet.write_merge(lig, lig, 1, 4, u'Entreprise : %s' % (blt.entreprise), gros)
    sheet.row(lig).height = sheet.row(lig).height * 3 / 2
    lig += 1
    sheet.write_merge(lig, lig, 1, 4, u'Adresse : %s' % (blt.entreprise.description), normal)
    lig += 1
    
    sheet.write_merge(lig, lig, 1, 4, u'Tuteur : %s' % (blt.tuteur.get_profile().nom_complet), gros)
    sheet.row(lig).height = sheet.row(lig).height * 3 / 2
    lig += 1
    sheet.write_merge(lig, lig, 1, 4, u'N° de tél portable : %s Adresse email : %s' % (blt.tuteur.get_profile().phone_number, blt.tuteur.email), normal)
    lig += 1
    normal = easyxf('font: name Arial, bold on, height 180; borders: left medium, right medium, bottom medium')
    sheet.write_merge(lig, lig, 1, 4, u'Chargé de promotion : %s' % (blt.formateur.get_profile().nom_complet), normal)
    
    titre = easyxf('font: name Arial, bold on, height 160; borders: left medium, top medium, right medium, bottom medium; align: horiz centre, vert centre')
    titrev = easyxf('font: name Arial, bold on, height 160; borders: left medium, top medium, right medium, bottom medium; align: horiz centre, vert centre; pattern: pattern solid, fore-colour green')
    lig = 13
    sheet.row(lig).height = sheet.row(lig).height * 5 / 2
    sheet.write(lig, 1, u'Capacités professionnelles et Tâches professionnelles (Être capable de...)', titrev)
    sheet.write(lig, 2, u'1ère année', titre)
    sheet.write(lig, 3, u'2ème année', titre)
    sheet.write(lig, 4, u'3ème année', titre)
    sheet.write(lig, 5, u'Résultats - Indicateurs de performance - Validation\r\n(Action réalisées ou initiées en entreprise)\r\n1ère année', titre)
    sheet.write(lig, 6, u'Résultats - Indicateurs de performance - Validation\r\n(Action réalisées ou initiées en entreprise)\r\n2ème année', titre)
    sheet.write(lig, 7, u'Résultats - Indicateurs de performance - Validation\r\n(Action réalisées ou initiées en entreprise)\r\n3ème année', titre)

    titre = easyxf('font: name Arial, bold on, height 160; borders: left medium, top medium, right medium, bottom medium; align: vert centre, horiz centre; pattern: pattern solid, fore-colour grey25')
    titreg = easyxf('font: name Arial, bold on, height 160; borders: left medium, top medium, right medium, bottom medium; align: vert centre; pattern: pattern solid, fore-colour grey25')
    normal = easyxf('font: name Arial, height 160; borders: left medium, top medium, right medium, bottom medium; align: vert centre, wrap true')
    commentaire = easyxf('font: name Arial, height 160; borders: left medium, top medium, right medium, bottom medium; align: vert top, wrap true')
    centre = easyxf('font: name Arial, height 160; borders: left medium, top medium, right medium, bottom medium; align: vert centre, horiz centre')
    note = easyxf('font: name Arial, height 160, bold on; align: vert centre')
    notec = easyxf('font: name Arial, height 160, bold on; align: vert centre, horiz centre')

    vertical = easyxf('font: name Arial, bold on, height 160; borders: left medium, top medium, right medium, bottom medium; align: horiz centre, vert centre, rotation 90')

    centrer = easyxf('font: name Arial, height 160; borders: left medium, top medium, right medium, bottom medium; align: vert centre, horiz centre; pattern: pattern solid, fore-colour red')
    centrev = easyxf('font: name Arial, height 160; borders: left medium, top medium, right medium, bottom medium; align: vert centre, horiz centre; pattern: pattern solid, fore-colour green')
    centreb = easyxf('font: name Arial, height 160; borders: left medium, top medium, right medium, bottom medium; align: vert centre, horiz centre; pattern: pattern solid, fore-colour blue')
    
    lig += 1
    
    for theme in Theme.objects.filter(grille = blt.grille):
        th_start = lig
        for ens in EnsembleCapacite.objects.filter(grille = blt.grille, theme = theme):
            sheet.write_merge(lig, lig, 1, 7, u'%d %s' % (ens.numero, ens.libelle), titreg)
            lig += 1
            start = lig
            for cap in Capacite.objects.filter(ensemble = ens).order_by('numero'):
                sheet.row(lig).height = sheet.row(lig).height * 3 / 2
                sheet.write(lig, 1, u'%d.%d %s' % (ens.numero, cap.numero, cap.libelle), normal)            
                notes = Evaluation.objects.filter(bulletin=blt, capacite=cap)
                sheet.write(lig, 2, evaluation(notes.filter(annee=0)), centre)
                sheet.write(lig, 3, evaluation(notes.filter(annee=1)), centre)
                sheet.write(lig, 4, evaluation(notes.filter(annee=2)), centre)
                lig += 1

            comm = Commentaire.objects.filter(bulletin=blt, ensemble=ens, annee=0)
            if comm:
                sheet.write_merge(start, lig - 1, 5, 5, comm[0].texte, commentaire)
            else:
                sheet.merge(start, lig - 1, 5, 5, commentaire)
            comm = Commentaire.objects.filter(bulletin=blt, ensemble=ens, annee=1)
            if comm:
                sheet.write_merge(start, lig - 1, 6, 6, comm[0].texte, commentaire)
            else:
                sheet.merge(start, lig - 1, 6, 6, commentaire)
            comm = Commentaire.objects.filter(bulletin=blt, ensemble=ens, annee=2)
            if comm:
                sheet.write_merge(start, lig - 1, 7, 7, comm[0].texte, commentaire)
            else:
                sheet.merge(start, lig - 1, 7, 7, commentaire)
            lig += 1

        th_end = lig - 1
        sheet.write_merge(th_start, th_end, 0, 0, theme.libelle, vertical)

    # Fin de tableau avec les moyennes et les savoirs etre
    lig += 1
    titreg = easyxf('font: name Arial, bold on, height 160; borders: left medium, top medium, right medium, bottom medium; align: vert centre; pattern: pattern solid, fore-colour sea_green')
    sheet.write(lig, 1, u'Note globale "compétence" sur 20 (sera entre 4 et 20)', titreg)
    gras = easyxf('font: name Arial, bold on, height 160; borders: left medium, top medium, right medium, bottom medium; align: vert centre, horiz centre; pattern: pattern solid, fore-colour sea_green')
    moyenne = Moyenne.objects.filter(bulletin=blt, annee=0)
    sheet.write(lig, 2, moyenne and moyenne[0].valeur_cp or 4, gras)
    moyenne = Moyenne.objects.filter(bulletin=blt, annee=1)
    sheet.write(lig, 3, moyenne and moyenne[0].valeur_cp or 4, gras)
    moyenne = Moyenne.objects.filter(bulletin=blt, annee=2)
    sheet.write(lig, 4, moyenne and moyenne[0].valeur_cp or 4, gras)

    lig += 2
    titre = easyxf('font: name Arial, bold on, height 160; borders: left medium, top medium, right medium, bottom medium; align: horiz centre, vert centre; pattern: pattern solid, fore-colour pink')
    normal = easyxf('font: name Arial, height 160; borders: left medium, top medium, right medium, bottom medium; align: vert centre; pattern: pattern solid, fore-colour pink')
    sheet.write(lig, 1, u'Savoir être', titre)
    sheet.write(lig, 2, u'', centrer)
    sheet.write(lig, 3, u'', centrev)
    sheet.write(lig, 4, u'', centreb)

    lig += 1
    start = lig
    centrer = easyxf('font: name Arial, bold on, height 160; borders: left medium, top medium, right medium, bottom medium; align: vert centre, horiz centre; pattern: pattern solid, fore-colour red')
    centrev = easyxf('font: name Arial, bold on, height 160; borders: left medium, top medium, right medium, bottom medium; align: vert centre, horiz centre; pattern: pattern solid, fore-colour green')
    centreb = easyxf('font: name Arial, bold on, height 160; borders: left medium, top medium, right medium, bottom medium; align: vert centre, horiz centre; pattern: pattern solid, fore-colour blue')
    savoirs = SavoirEtre.objects.filter(grille=blt.grille)
    for sv in savoirs:
        sheet.row(lig).height = sheet.row(lig).height * 3 / 2
        sheet.write(lig, 1, sv.libelle, normal)
        notes = Note.objects.filter(bulletin=blt, savoir=sv)
        n = notes.filter(annee=0)
        sheet.write(lig, 2, n and n[0].valeur or '', centrer)
        n = notes.filter(annee=1)
        sheet.write(lig, 3, n and n[0].valeur or '', centrev)
        n = notes.filter(annee=2)
        sheet.write(lig, 4, n and n[0].valeur or '', centreb)
        lig += 1

    normal = easyxf('font: name Arial, bold on, height 180; borders: left medium, right medium, bottom medium, top medium; align: vert top, wrap true')
    sheet.write_merge(start, lig - 1, 5, 6, u'Commentaires généraux :\r\n%s' % blt.commentaires_generaux, normal)

    lig += 1
    titreg = easyxf('font: name Arial, bold on, height 160; borders: left medium, top medium, right medium, bottom medium; align: vert centre; pattern: pattern solid, fore-colour light_blue')
    sheet.write(lig, 1, u'Moyenne "savoir être" (sur 20)', titreg)
    moyenne = Moyenne.objects.filter(bulletin=blt, annee=0)
    sheet.write(lig, 2, moyenne and moyenne[0].valeur_sv or 4, centrer)
    moyenne = Moyenne.objects.filter(bulletin=blt, annee=1)
    sheet.write(lig, 3, moyenne and moyenne[0].valeur_sv or 4, centrev)
    moyenne = Moyenne.objects.filter(bulletin=blt, annee=2)
    sheet.write(lig, 4, moyenne and moyenne[0].valeur_sv or 4, centreb)
    
    lig += 1
    titreg = easyxf('font: name Arial, bold on, height 200; borders: left medium, top medium, right medium, bottom medium; align: vert centre; pattern: pattern solid, fore-colour light_blue')
    centrer = easyxf('font: name Arial, bold on, height 200; borders: left medium, top medium, right medium, bottom medium; align: vert centre, horiz centre; pattern: pattern solid, fore-colour red')
    centrev = easyxf('font: name Arial, bold on, height 200; borders: left medium, top medium, right medium, bottom medium; align: vert centre, horiz centre; pattern: pattern solid, fore-colour green')
    centreb = easyxf('font: name Arial, bold on, height 200; borders: left medium, top medium, right medium, bottom medium; align: vert centre, horiz centre; pattern: pattern solid, fore-colour blue')
    sheet.row(lig).height = sheet.row(lig).height * 3 / 2
    sheet.write(lig, 1, u'Note entreprise (sur 20)', titreg)
    moyenne = Moyenne.objects.filter(bulletin=blt, annee=0)
    sheet.write(lig, 2, moyenne and moyenne[0].valeur_gn or 4, centrer)
    moyenne = Moyenne.objects.filter(bulletin=blt, annee=1)
    sheet.write(lig, 3, moyenne and moyenne[0].valeur_gn or 4, centrev)
    moyenne = Moyenne.objects.filter(bulletin=blt, annee=2)
    sheet.write(lig, 4, moyenne and moyenne[0].valeur_gn or 4, centreb)

    book.save(response)
    return response
