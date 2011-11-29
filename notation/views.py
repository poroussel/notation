# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.http import urlquote
from django.views.generic.create_update import update_object, create_object
from django.core.urlresolvers import reverse
from cfai.notation.models import *
from cfai.notation.forms import *
from xlwt import *
from datetime import date

@user_passes_test(lambda u: u.is_authenticated() and u.get_profile().is_tuteur())
def index_tuteur(request):
    bulletins = Bulletin.objects.filter(tuteur=request.user)
    return render_to_response('index_tuteur.html', RequestContext(request, {'bulletins' : bulletins}))

@user_passes_test(lambda u: u.is_authenticated() and u.get_profile().is_administratif())
def index_admin(request):
    return render_to_response('index_admin.html', RequestContext(request))

@user_passes_test(lambda u: u.is_authenticated() and u.get_profile().is_administratif())
def index_gestion(request):
    return render_to_response('index_gestion.html', RequestContext(request))

@user_passes_test(lambda u: u.is_authenticated() and u.get_profile().is_administratif())
def index_assistance(request):
    """
    Liste les formations ayant au moins une session en cours et pour
    chacune les sessions en cours.
    """
    annee = date.today().year
    formations = Formation.objects.all()
    return render_to_response('index_assistance.html', RequestContext(request, {'formations' : formations}))

@user_passes_test(lambda u: u.is_authenticated() and u.get_profile().is_formateur())
def index_formateur(request):
    bulletins = Bulletin.objects.filter(formateur=request.user)
    return render_to_response('index_formateur.html', RequestContext(request, {'bulletins' : bulletins}))

@user_passes_test(lambda u: u.is_authenticated() and u.get_profile().is_eleve())
def index_eleve(request):
    bulletins = Bulletin.objects.filter(eleve=request.user)
    return render_to_response('index_eleve.html', RequestContext(request, {'bulletins' : bulletins}))

@login_required
def index(request):
    profile = request.user.get_profile()
    if not profile.password_modified:
        messages.warning(request, u'Vous devez modifier votre mot de passe !')

    if profile.is_tuteur():
        return HttpResponseRedirect(reverse(index_tuteur))
    if profile.is_administratif():
        return HttpResponseRedirect(reverse(index_admin))
    if profile.is_formateur():
        return HttpResponseRedirect(reverse(index_formateur))
    if profile.is_eleve():
        return HttpResponseRedirect(reverse(index_eleve))
    return render_to_response('index.html', RequestContext(request))

def bulletin_xls(request, blt):
    response = HttpResponse(mimetype='application/xls')
    response['Content-Disposition'] = 'attachment; filename="%s.xls"' % blt.eleve.get_full_name()

    # Creation d'un workbook en Unicode
    book = Workbook(encoding='cp1251')
    sheet = book.add_sheet('Bulletin %d-%d' % (blt.grille.promotion, blt.grille.promotion + blt.grille.duree - 1))

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

@login_required
def bulletin(request, blt_id):
    blt = get_object_or_404(Bulletin, pk=blt_id)
    # annees = [0, 1, 2] pour une formation de 3 ans
    annees = range(blt.grille.duree)
    ens = EnsembleCapacite.objects.filter(grille=blt.grille)
    
    if request.GET.get('format', None) == 'xls':
        return bulletin_xls(request, blt)
    
    return render_to_response('notation/bulletin.html', RequestContext(request, {'bulletin' : blt, 'ens' : ens, 'annees' : annees}))

@login_required
def annee_bulletin(request, blt_id, annee):
    blt = get_object_or_404(Bulletin, pk=blt_id)
    ens = EnsembleCapacite.objects.filter(grille=blt.grille)
    setre = SavoirEtre.objects.filter(grille=blt.grille)
    setre = [se for se in setre if se.valide(annee)]
    
    form = BulletinForm(commentaire=blt.commentaires_generaux, savoirs=setre, user=request.user)
    if request.method == 'POST':
        form = BulletinForm(request.POST, commentaire=blt.commentaires_generaux, savoirs=setre, user=request.user)
        if form.is_valid():
            if 'commentaires_generaux' in form.cleaned_data:
                blt.commentaires_generaux = form.cleaned_data['commentaires_generaux']
                blt.save()
    return render_to_response('notation/annee_bulletin.html', RequestContext(request, {'bulletin' : blt, 'annee' : annee, 'ens' : ens, 'form' : form}))

@login_required
def ensemble_bulletin(request, blt_id, annee, ens_id):
    blt = get_object_or_404(Bulletin, pk=blt_id)
    ens = get_object_or_404(EnsembleCapacite, pk=ens_id)
    capacites = Capacite.objects.filter(ensemble=ens)
    questions = [(x.id, x.libelle, x.cours) for x in capacites if x.valide(annee)]
    
    # L'utilisation de list() n'est pas nécessaire mais force l'exécution
    # du QuerySet afin déviter une requête imbriquée
    notes = Note.objects.filter(bulletin=blt, capacite__in=list(capacites), annee=annee)
    
    commentaires = Commentaire.objects.filter(bulletin=blt, ensemble=ens)
    if commentaires.count() > 0:
        commentaire = commentaires[0].texte
    else:
        commentaire = None

    # Code relativement gore et inefficace mais qui permet de naviguer
    # dans les ensembles en évitant les ensembles vides (dépendant de l'année)
    suivant = ens.suivant()
    while suivant and len([cap for cap in Capacite.objects.filter(ensemble=suivant) if cap.valide(annee)]) == 0:
        suivant = suivant.suivant()
    precedent = ens.precedent()
    while precedent and len([cap for cap in Capacite.objects.filter(ensemble=precedent) if cap.valide(annee)]) == 0:
        precedent = precedent.precedent()

    if request.method == 'POST':
        form = NotationForm(request.POST, questions=questions, user=request.user)
        if form.is_valid():
            if 'commentaire' in form.cleaned_data:
                com, created = Commentaire.objects.get_or_create(bulletin=blt, ensemble=ens, defaults={'texte' : form.cleaned_data['commentaire'], 'auteur_modification' : request.user})
                if not created:
                    com.texte = form.cleaned_data['commentaire']
                    com.save()
                        
            for (capid, libelle, cours) in questions:
                if str(capid) in form.cleaned_data:
                    value = form.cleaned_data[str(capid)]
                    cap = Capacite.objects.get(id=capid)
                    if value:
                        note, created = Note.objects.get_or_create(bulletin=blt, capacite=cap, defaults={'valeur' : value, 'annee' : annee, 'auteur_modification' : request.user})
                        if not created:
                            note.valeur = value
                            note.save()
                    else:
                        Note.objects.filter(bulletin=blt, capacite=cap).delete()
                        
            blt.maj_moyennes()
            if suivant:
                return HttpResponseRedirect(reverse(ensemble_bulletin, args=[blt_id, annee, suivant.id]))
            return HttpResponseRedirect(reverse(bulletin, args=[blt_id]))
    else:
        form = NotationForm(questions=questions, notes=notes, commentaire=commentaire, user=request.user)
    return render_to_response('notation/ensemble.html', RequestContext(request, {'ensemble' : ens,
                                                                                 'annee' : annee,
                                                                                 'bulletin' : blt,
                                                                                 'form' : form,
                                                                                 'precedent' : precedent,
                                                                                 'suivant' : suivant}))

@login_required
def motdepasse(request):
    if request.method == 'POST':
        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            profile = user.get_profile()
            profile.password_modified = True
            profile.save()
            messages.success(request, u'Votre mot de passe a été mis à jour.')
            logout(request)
            return HttpResponseRedirect(reverse(index))
    else:
        password_form = PasswordChangeForm(None)
    return render_to_response('notation/motdepasse.html', RequestContext(request, {'password_form' : password_form}))

@login_required
def profil(request):
    if request.method == 'POST':
        form = ProfilUtilisateurForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, u'Votre profil a été mis à jour.')
            return HttpResponseRedirect(reverse(index))
    else:
        form = ProfilUtilisateurForm(instance=request.user)
    return render_to_response('notation/profil.html', RequestContext(request, {'password_form' : form}))


@login_required
def ajouter_eleve(request):
    if request.method == 'POST':
        form = CreationEleveForm(request.POST)
        if form.is_valid():
            eleve = User()
            eleve.username = form.cleaned_data['identifiant']
            eleve.set_password(form.cleaned_data['identifiant'])
            eleve.first_name = form.cleaned_data['prenom']
            eleve.last_name = form.cleaned_data['nom']
            eleve.email = form.cleaned_data['email']
            eleve.is_active = True
            eleve.save()
            # Le profil par défaut est élève, pas besoin de le spécifier
            bulletin = Bulletin()
            bulletin.eleve = eleve
            bulletin.grille = form.cleaned_data['formation']
            bulletin.entreprise = form.cleaned_data['entreprise']
            bulletin.tuteur = form.cleaned_data['tuteur']
            bulletin.formateur = form.cleaned_data['formateur']
            bulletin.save()
            if '_continuer' in request.POST:
                return HttpResponseRedirect(reverse('ajouter_eleve'))
            return HttpResponseRedirect(reverse('liste_eleve'))
    else:
        form = CreationEleveForm()
    return render_to_response('notation/eleve_form.html', RequestContext(request, {'form' : form, 'blt' : None}))

@login_required
def modifier_eleve(request, object_id):
    """
    On gère la relation élève-bulletin (et donc élève-formation) comme
    si elle était unique. La base permet d'avoir plusieurs bulletins pour
    un élève, si cela s'avère utile il faudra modifier l'interface de saisie.
    """
    elv = get_object_or_404(User, pk=object_id)
    blt = Bulletin.objects.get(eleve=elv)
    if request.method == 'POST':
        form = EditionEleveForm(request.POST)
        if form.is_valid():
            elv.first_name = form.cleaned_data['prenom']
            elv.last_name = form.cleaned_data['nom']
            elv.email = form.cleaned_data['email']
            elv.save()
            blt.entreprise = form.cleaned_data['entreprise']
            blt.tuteur = form.cleaned_data['tuteur']
            blt.formateur = form.cleaned_data['formateur']
            blt.save()
            return HttpResponseRedirect(reverse('liste_eleve'))
    else:
        form = EditionEleveForm(initial={'identifiant' : elv.username,
                                         'prenom' : elv.first_name,
                                         'nom' : elv.last_name,
                                         'email' : elv.email,
                                         'entreprise' : blt.entreprise,
                                         'tuteur' : blt.tuteur,
                                         'formateur' : blt.formateur})
    return render_to_response('notation/eleve_form.html', RequestContext(request, {'form' : form, 'blt' : blt}))

@login_required
def ajouter_tuteur(request):
    if request.method == 'POST':
        form = UtilisateurForm(request.POST)
        if form.is_valid():
            tuteur = form.save()
            profil = ProfilUtilisateur.objects.get(user=tuteur)
            profil.user_type = 't'
            profil.save()
            if '_continuer' in request.POST:
                return HttpResponseRedirect(reverse('ajouter_tuteur'))
            return HttpResponseRedirect(reverse('liste_tuteur'))
    else:
        form = UtilisateurForm()
    return render_to_response('notation/tuteur_form.html', RequestContext(request, {'form' : form}))

@login_required
def ajouter_formateur(request):
    if request.method == 'POST':
        form = UtilisateurForm(request.POST)
        if form.is_valid():
            formateur = form.save()
            profil = ProfilUtilisateur.objects.get(user=formateur)
            profil.user_type = 'f'
            profil.save()
            if '_continuer' in request.POST:
                return HttpResponseRedirect(reverse('ajouter_formateur'))
            return HttpResponseRedirect(reverse('liste_formateur'))
    else:
        form = UtilisateurForm()
    return render_to_response('notation/formateur_form.html', RequestContext(request, {'form' : form}))

@login_required
def detail_entreprise(request, object_id=None):
    psr = reverse('liste_entreprise')
    if object_id:
        return update_object(request, form_class=EntrepriseForm, object_id=object_id, post_save_redirect=psr)
    if '_addanother' in request.POST:
        psr = reverse('ajouter_entreprise')
    return create_object(request, form_class=EntrepriseForm, post_save_redirect=psr)

@login_required
def detail_formateur(request, object_id):
    frm = get_object_or_404(User, pk=object_id)
    bulletins = Bulletin.objects.filter(formateur=frm)
    return update_object(request,
                         form_class=UtilisateurForm,
                         object_id=object_id,
                         post_save_redirect=reverse('liste_formateur'),
                         template_name='notation/formateur_form.html',
                         extra_context={'bulletins' : bulletins})

@login_required
def detail_tuteur(request, object_id):
    frm = get_object_or_404(User, pk=object_id)
    bulletins = Bulletin.objects.filter(tuteur=frm)
    return update_object(request,
                         form_class=UtilisateurForm,
                         object_id=object_id,
                         post_save_redirect=reverse('liste_tuteur'),
                         template_name='notation/tuteur_form.html',
                         extra_context={'bulletins' : bulletins})


@login_required
def recherche(request):
    # FIXME : les résultats doivent dépendrent de l'utilisateur courant
    search = request.GET.get('search', '')
    if search == '':
        search = 'rien'
    ol = list(Entreprise.objects.filter(nom__istartswith=search))
    ol += list(Bulletin.objects.filter(grille__formation__istartswith=search))
    # Liste des bulletins qui référencent l'entreprise
    ol += list(Bulletin.objects.filter(entreprise__nom__istartswith=search))
    # Liste des bulletins qui référencent l'eleve
    ol += list(Bulletin.objects.filter(eleve__last_name__istartswith=search))
    ol += list(Bulletin.objects.filter(eleve__first_name__istartswith=search))
    
    return render_to_response('search.html', RequestContext(request, {'object_list' : ol, 'search_str' : search}))

class SearchMiddleware(object):
    def process_request(self, request):
        if request.method == 'POST' and '_search' in request.POST:
            chaine =  urlquote(request.POST['chaine'])
            return HttpResponseRedirect(reverse(recherche) + '?search=%s' % chaine)
        return None
