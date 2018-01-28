# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import render, render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.http import urlquote
from django.views.generic.create_update import update_object, create_object
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from cfai.notation.models import *
from cfai.notation.forms import *
from cfai.notation.excel import *

@user_passes_test(lambda u: u.is_authenticated() and u.get_profile().is_administratif())
def suppression_objet(request, model, object_id):
    """
    model est une chaîne de caractères représentant le nom
    du modèle, par exemple CommandeClient.
    """
    user_type = ContentType.objects.get(model=model.lower())
    obj = user_type.get_object_for_this_type(pk=object_id)
    form = SuppressionForm()
    if request.method == 'POST':
        form = SuppressionForm(request.POST)
        if form.is_valid():
            supprimer_objet(obj, request.user, form.cleaned_data['raison'])
            if 'next' in request.GET:
                return HttpResponseRedirect(request.GET['next'])
            return HttpResponseRedirect(reverse(index))
    return render_to_response('notation/suppression_form.html', RequestContext(request, {'object': obj, 'classe': user_type, 'form': form}))

@user_passes_test(lambda u: u.is_authenticated() and u.get_profile().is_tuteur())
def index_tuteur(request):
    bulletins = Bulletin.objects.filter(tuteur=request.user)
    return render_to_response('index_tuteur.html', RequestContext(request, {'bulletins' : bulletins}))

@user_passes_test(lambda u: u.is_authenticated() and u.get_profile().is_manitou())
def index_admin(request):
    return render_to_response('index_admin.html', RequestContext(request))

@user_passes_test(lambda u: u.is_authenticated() and u.get_profile().is_manitou())
def index_gestion(request):
    return render_to_response('index_gestion.html', RequestContext(request))

@user_passes_test(lambda u: u.is_authenticated() and (u.get_profile().is_manitou() or u.get_profile().is_formateur()))
def index_assistance(request):
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
    if profile.is_tuteur():
        return HttpResponseRedirect(reverse(index_tuteur))
    if profile.is_manitou() and not profile.is_formateur():
        return HttpResponseRedirect(reverse(index_admin))
    if profile.is_formateur():
        return HttpResponseRedirect(reverse(index_formateur))
    if profile.is_eleve():
        return HttpResponseRedirect(reverse(index_eleve))
    return render_to_response('index.html', RequestContext(request))

@user_passes_test(lambda u: u.is_authenticated() and not u.get_profile().is_eleve())
def resume_grille(request, object_id, annee):
    """
    Affiche les résultats des apprentis de la grille dans un tableau récapitulatif
    """
    grille = get_object_or_404(GrilleNotation, pk=object_id)
    bulletins = Bulletin.objects.select_related().filter(grille=grille).order_by('eleve__last_name')
    moyennes_annee = Moyenne.objects.filter(annee=annee)
    lignes = list()
    for bulletin in bulletins:
        moyenne = moyennes_annee.filter(bulletin=bulletin)
        if moyenne:
            lignes.append((bulletin, moyenne[0].valeur_cp, moyenne[0].valeur_sv, moyenne[0].valeur_gn))
        else:
            lignes.append((bulletin, 0, 0, 0))
    return render_to_response('notation/resume_grille.html', RequestContext(request, {'grille' : grille, 'lignes' : lignes, 'annee' : annee}))

def check_auth_blt(request, blt):
    profil = request.user.get_profile()
    if profil.is_eleve() and profil.user != blt.eleve:
        messages.warning(request, u'Eh, il semblerait que cette page ne vous soit pas accessible ! Retour à la case départ.')
        return False
    return True

@login_required
def bulletin(request, blt_id):
    blt = Bulletin.tous.get(pk=blt_id)
    if not check_auth_blt(request, blt):
        return HttpResponseRedirect(reverse(index))
    if request.GET.get('format', None) == 'xls':
        return bulletin_xls(request, blt)

    if request.method == 'POST':
        form = PJForm(request.POST, request.FILES)
        if form.is_valid():
            pj = form.save(commit=False)
            pj.bulletin = blt
            pj.save()
            form = PJForm()
            messages.success(request, u'Fichier ajouté au bulletin.')
    else:
        form = PJForm()
    annees = range(blt.grille.duree)
    pjs = PieceJointe.objects.filter(bulletin=blt)
    return render(request, 'notation/bulletin.html', {
        'bulletin' : blt,
        'annees' : annees,
        'pjs': pjs,
        'form': form,
    })

@user_passes_test(lambda u: u.is_authenticated())
def annee_bulletin(request, blt_id, annee):
    """
    Affiche les themes d'une grille de notation avec pour chaque
    thème les ensembles de capacités et une note pour une annnée,
    le formulaire de saisie des savoirs être ainsi que les moyennes
    actuelles pour l'année.
    """
    blt = Bulletin.tous.get(pk=blt_id)
    if not check_auth_blt(request, blt):
        return HttpResponseRedirect(reverse(index))
    themes = Theme.objects.filter(grille=blt.grille).select_related()
    pourcentage = {}
    for th in themes:
        pourcentage[th] = blt.pourcentage_saisie(annee, th)
    setre = blt.grille.savoiretre_set.all()
    notes = Note.objects.filter(bulletin=blt, savoir__in=list(setre), annee=annee)
    notesth = Note.objects.filter(bulletin=blt, theme__in=list(themes), annee=annee)
    moyenne = Moyenne.objects.filter(annee=annee, bulletin=blt)
    commentaire = CommentaireGeneral.objects.filter(annee=annee, bulletin=blt)
    commentaire = bool(commentaire) and commentaire[0].texte or None

    thform = NotationThemeForm(prefix='themes', themes=themes, user=request.user, notes=notesth, prc=pourcentage)
    form = BulletinForm(commentaire=commentaire, notes=notes, savoirs=setre, user=request.user)

    if request.method == 'POST':
        if 'themes' in request.POST:
            thform = NotationThemeForm(request.POST, prefix='themes', themes=themes, user=request.user, prc=pourcentage)
            if thform.is_valid():
                for th in themes:
                    if str(th.id) in thform.cleaned_data:
                        value = thform.cleaned_data[str(th.id)]
                        if value:
                            note, created = Note.objects.get_or_create(bulletin=blt, theme=th, annee=annee, defaults={'valeur' : value, 'auteur_modification' : request.user})
                            if not created:
                                note.valeur = value
                                note.auteur_modification = request.user
                                note.save()
                blt.calcul_moyenne_competence(annee, request.user)

        else:
            form = BulletinForm(request.POST, commentaire=blt.commentaires_generaux, savoirs=setre, user=request.user)
            if form.is_valid():
                if 'commentaires_generaux' in form.cleaned_data:
                    value = form.cleaned_data['commentaires_generaux']
                    comm, created = CommentaireGeneral.objects.get_or_create(bulletin=blt, annee=annee, defaults={'texte' : value, 'auteur_modification' : request.user})
                    if not created:
                        comm.texte = value
                        comm.auteur_modification = request.user
                        comm.save()

                for sv in setre:
                    if str(sv.id) in form.cleaned_data:
                        value = form.cleaned_data[str(sv.id)]
                        if value:
                            note, created = Note.objects.get_or_create(bulletin=blt, savoir=sv, annee=annee, defaults={'valeur' : value, 'auteur_modification' : request.user})
                            if not created:
                                note.valeur = value
                                note.auteur_modification = request.user
                                note.save()
                blt.calcul_moyenne_savoir(annee, request.user)

    return render_to_response('notation/annee_bulletin.html', RequestContext(request, {'bulletin' : blt, 'annee' : annee, 'themes' : themes, 'form' : form, 'moyenne' : moyenne, 'thform' : thform}))

@user_passes_test(lambda u: u.is_authenticated() and (u.get_profile().is_manitou() or u.get_profile().is_tuteur() or u.get_profile().is_eleve()))
def ensemble_bulletin(request, blt_id, annee, ens_id):
    blt = Bulletin.tous.get(pk=blt_id)
    if not check_auth_blt(request, blt):
        return HttpResponseRedirect(reverse(index))
    ens = get_object_or_404(EnsembleCapacite, pk=ens_id)
    capacites = ens.capacite_set.all()
    evaluations = Evaluation.objects.filter(bulletin=blt, capacite__in=list(capacites), annee=annee)

    commentaires = Commentaire.objects.filter(bulletin=blt, ensemble=ens, annee=annee)
    commentaire = commentaires and commentaires[0].texte or None

    suivant = ens.suivant()
    precedent = ens.precedent()

    if request.method == 'POST':
        form = NotationForm(request.POST, questions=capacites, user=request.user)
        if form.is_valid():
            if 'commentaire' in form.cleaned_data:
                com, created = Commentaire.objects.get_or_create(bulletin=blt, ensemble=ens, annee=annee, defaults={'texte' : form.cleaned_data['commentaire'], 'auteur_modification' : request.user})
                if not created:
                    com.texte = form.cleaned_data['commentaire']
                    com.save()

            for cap in capacites:
                if str(cap.id) in form.cleaned_data:
                    value = form.cleaned_data[str(cap.id)]
                    if value and value in dict(APPRECIATIONS).keys():
                        note, created = Evaluation.objects.get_or_create(bulletin=blt, capacite=cap, annee=annee, defaults={'valeur' : value, 'auteur_modification' : request.user})
                        if not created:
                            note.valeur = value
                            note.auteur_modification = request.user
                            note.save()

            if suivant:
                return HttpResponseRedirect(reverse(ensemble_bulletin, args=[blt_id, annee, suivant.id]))
            return HttpResponseRedirect(reverse(bulletin, args=[blt_id]))
    else:
        form = NotationForm(questions=capacites, notes=evaluations, commentaire=commentaire, user=request.user)
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
    profil = request.user.get_profile()
    if request.method == 'POST':
        form = ProfilUtilisateurForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            profil.phone_number = form.cleaned_data['phone_number']
            profil.save()
            messages.success(request, u'Votre profil a été mis à jour.')
            return HttpResponseRedirect(reverse(index))
    else:
        form = ProfilUtilisateurForm(instance=request.user, initial={'phone_number' : profil.phone_number})
    return render_to_response('notation/profil.html', RequestContext(request, {'password_form' : form}))

def mail_new_user(request, user, password):
    body = render_to_string('creation_compte.txt', {'profil' : user.get_profile(), 'site' : Site.objects.get_current(), 'password': password})
    try:
        user.email_user(u'[CFAI/ENSMM] Création de votre compte', body, from_email=settings.SERVER_EMAIL)
        messages.success(request, u'Un email a été envoyé à %s.' % user.get_full_name())
    except:
        messages.error(request, u'Une erreur s\'est produite lors de l\'envoi d\'un email à %s, veuillez vérifier l\'adresse.' % user.email)
        return False
    return True

def mail_new_password(request, user):
    profile = user.get_profile()
    password = User.objects.make_random_password()
    user.set_password(password)
    user.save()
    profile.password_modified = False
    profile.save()
    body = render_to_string('maj_compte.txt', {'profil' : profile, 'site' : Site.objects.get_current(), 'password' : password})
    try:
        user.email_user(u'[CFAI/ENSMM] Réinitialisation de votre compte', body, from_email=settings.SERVER_EMAIL)
        messages.success(request, u'Un email a été envoyé à %s.' % user.get_full_name())
    except:
        messages.error(request, u'Une erreur s\'est produite lors de l\'envoi d\'un email à %s, veuillez vérifier l\'adresse.' % user.email)
        return False
    return True

@user_passes_test(lambda u: u.is_authenticated() and u.get_profile().is_administratif())
def ajouter_eleve(request):
    if request.method == 'POST':
        form = CreationEleveForm(request.POST)
        if form.is_valid():
            eleve = User()
            eleve.username = form.cleaned_data['identifiant']
            password = User.objects.make_random_password()
            eleve.set_password(password)
            eleve.first_name = form.cleaned_data['prenom']
            eleve.last_name = form.cleaned_data['nom']
            eleve.email = form.cleaned_data['email']
            eleve.is_active = True
            eleve.save()
            # Le profil par défaut est élève, pas besoin de le spécifier
            profil = eleve.get_profile()
            profil.phone_number = form.cleaned_data['telephone']
            profil.save()
            bulletin = Bulletin()
            bulletin.eleve = eleve
            bulletin.grille = form.cleaned_data['formation']
            bulletin.entreprise = form.cleaned_data['entreprise']
            bulletin.tuteur = form.cleaned_data['tuteur']
            bulletin.formateur = form.cleaned_data['formateur']
            bulletin.save()

            if not mail_new_user(request, eleve, password):
                return HttpResponseRedirect(reverse('detail_eleve', args=[eleve.id]))

            if '_continuer' in request.POST:
                return HttpResponseRedirect(reverse('ajouter_eleve'))
            return HttpResponseRedirect(reverse('liste_eleve'))
    else:
        form = CreationEleveForm()
    return render_to_response('notation/eleve_form.html', RequestContext(request, {'form' : form, 'blt' : None}))

@user_passes_test(lambda u: u.is_authenticated() and u.get_profile().is_manitou())
def modifier_eleve(request, object_id):
    """
    On gère la relation élève-bulletin (et donc élève-formation) comme
    si elle était unique. La base permet d'avoir plusieurs bulletins pour
    un élève, si cela s'avère utile il faudra modifier l'interface de saisie.
    """
    elv = get_object_or_404(User, pk=object_id)
    profil = elv.get_profile()
    blts = Bulletin.tous.filter(eleve=elv).order_by('-id')
    blt = blts[0]
    if request.method == 'POST':
        if '_supprimer' in request.POST:
            return HttpResponseRedirect(reverse(suppression_objet, args=['ProfilUtilisateur', profil.id]))
        form = EditionEleveForm(request.POST)
        if form.is_valid():
            elv.first_name = form.cleaned_data['prenom']
            elv.last_name = form.cleaned_data['nom']
            elv.email = form.cleaned_data['email']
            elv.save()
            profil.phone_number = form.cleaned_data['telephone']
            profil.save()
            blt.entreprise = form.cleaned_data['entreprise']
            blt.tuteur = form.cleaned_data['tuteur']
            blt.formateur = form.cleaned_data['formateur']
            blt.save()


            if '_reinit' in request.POST and not mail_new_password(request, elv):
                return render_to_response('notation/eleve_form.html', RequestContext(request, {'form' : form, 'blt' : blts, 'object' : elv, 'profil' : profil}))

            return HttpResponseRedirect(reverse('liste_eleve'))
    else:
        form = EditionEleveForm(initial={'identifiant' : elv.username,
                                         'prenom' : elv.first_name,
                                         'nom' : elv.last_name,
                                         'email' : elv.email,
                                         'entreprise' : blt.entreprise,
                                         'tuteur' : blt.tuteur,
                                         'formateur' : blt.formateur,
                                         'telephone' : profil.phone_number})
    return render_to_response('notation/eleve_form.html', RequestContext(request, {'form' : form, 'blt' : blts, 'object' : elv, 'profil' : profil}))

@user_passes_test(lambda u: u.is_authenticated() and u.get_profile().is_administratif())
def ajouter_tuteur(request):
    if request.method == 'POST':
        form = UtilisateurForm(request.POST)
        if form.is_valid():
            tuteur = form.save()
            password = User.objects.make_random_password()
            tuteur.set_password(password)
            tuteur.save()
            profil = ProfilUtilisateur.objects.get(user=tuteur)
            profil.user_type = 't'
            profil.phone_number = form.cleaned_data['phone_number']
            profil.save()

            if not mail_new_user(request, tuteur, password):
                return HttpResponseRedirect(reverse('detail_tuteur', args=[tuteur.id]))

            if '_continuer' in request.POST:
                return HttpResponseRedirect(reverse('ajouter_tuteur'))
            return HttpResponseRedirect(reverse('liste_tuteur'))
    else:
        form = UtilisateurForm()
    return render_to_response('notation/tuteur_form.html', RequestContext(request, {'form' : form}))

@user_passes_test(lambda u: u.is_authenticated() and u.get_profile().is_administratif())
def ajouter_formateur(request):
    if request.method == 'POST':
        form = UtilisateurForm(request.POST)
        if form.is_valid():
            formateur = form.save()
            password = User.objects.make_random_password()
            formateur.set_password(password)
            formateur.save()
            profil = ProfilUtilisateur.objects.get(user=formateur)
            profil.user_type = 'f'
            profil.phone_number = form.cleaned_data['phone_number']
            profil.save()

            if not mail_new_user(request, formateur, password):
                return HttpResponseRedirect(reverse('detail_formateur', args=[formateur.id]))

            if '_continuer' in request.POST:
                return HttpResponseRedirect(reverse('ajouter_formateur'))
            return HttpResponseRedirect(reverse('liste_formateur'))
    else:
        form = UtilisateurForm()
    return render_to_response('notation/formateur_form.html', RequestContext(request, {'form' : form}))

@user_passes_test(lambda u: u.is_authenticated() and u.get_profile().is_administratif())
def ajouter_pilote(request):
    if request.method == 'POST':
        form = UtilisateurForm(request.POST)
        if form.is_valid():
            pilote = form.save()
            password = User.objects.make_random_password()
            pilote.set_password(password)
            pilote.save()
            profil = ProfilUtilisateur.objects.get(user=pilote)
            profil.user_type = 'p'
            profil.phone_number = form.cleaned_data['phone_number']
            profil.save()
            if not mail_new_user(request, pilote, password):
                return HttpResponseRedirect(reverse('detail_pilote', args=[pilote.id]))
            if '_continuer' in request.POST:
                return HttpResponseRedirect(reverse('ajouter_pilote'))
            return HttpResponseRedirect(reverse('liste_pilote'))
    else:
        form = UtilisateurForm()
    return render_to_response('notation/pilote_form.html', RequestContext(request, {'form' : form}))

@user_passes_test(lambda u: u.is_authenticated() and u.get_profile().is_administratif())
def detail_pilote(request, object_id):
    pilote = get_object_or_404(User, pk=object_id)
    profil = pilote.get_profile()
    if request.method == 'POST':
        if '_delete' in request.POST:
            return HttpResponseRedirect(reverse(suppression_objet, args=['ProfilUtilisateur', profil.id]))
        form = ProfilUtilisateurForm(request.POST, instance=pilote)
        if form.is_valid():
            pilote = form.save()
            profil.phone_number = form.cleaned_data['phone_number']
            profil.save()
            if '_reinit' in request.POST and not mail_new_password(request, pilote):
                return render_to_response('notation/pilote_form.html', RequestContext(request, {'form' : form, 'object' : pilote}))
            return HttpResponseRedirect(reverse('liste_pilote'))
    else:
        form = ProfilUtilisateurForm(instance=pilote, initial={'phone_number' : profil.phone_number})
    return render_to_response('notation/pilote_form.html', RequestContext(request, {'form' : form, 'object' : pilote}))

@user_passes_test(lambda u: u.is_authenticated() and u.get_profile().is_manitou())
def detail_entreprise(request, object_id=None):
    psr = reverse('liste_entreprise')
    if object_id:
        return update_object(request, form_class=EntrepriseForm, object_id=object_id, post_save_redirect=psr)
    if '_addanother' in request.POST:
        psr = reverse('ajouter_entreprise')
    return create_object(request, form_class=EntrepriseForm, post_save_redirect=psr)

@user_passes_test(lambda u: u.is_authenticated() and u.get_profile().is_manitou())
def detail_formateur(request, object_id):
    frm = get_object_or_404(User, pk=object_id)
    profil = frm.get_profile()
    bulletins = Bulletin.objects.filter(formateur=frm).order_by('grille', 'eleve__last_name', 'eleve__first_name')
    if request.method == 'POST':
        if '_delete' in request.POST:
            return HttpResponseRedirect(reverse(suppression_objet, args=['ProfilUtilisateur', profil.id]))
        form = ProfilUtilisateurForm(request.POST, instance=frm)
        if form.is_valid():
            formateur = form.save()
            profil.phone_number = form.cleaned_data['phone_number']
            profil.save()

            if '_reinit' in request.POST and not mail_new_password(request, formateur):
                return render_to_response('notation/formateur_form.html', RequestContext(request, {'form' : form, 'bulletins' : bulletins, 'object' : frm}))

            return HttpResponseRedirect(reverse('liste_formateur'))
    else:
        form = ProfilUtilisateurForm(instance=frm, initial={'phone_number' : profil.phone_number})
    return render_to_response('notation/formateur_form.html', RequestContext(request, {'form' : form, 'bulletins' : bulletins, 'object' : frm}))

@user_passes_test(lambda u: u.is_authenticated() and u.get_profile().is_manitou())
def detail_tuteur(request, object_id):
    tuteur = get_object_or_404(User, pk=object_id)
    profil = tuteur.get_profile()
    bulletins = Bulletin.objects.filter(tuteur=tuteur).order_by('grille', 'eleve__last_name', 'eleve__first_name')
    if request.method == 'POST':
        if '_delete' in request.POST:
            return HttpResponseRedirect(reverse(suppression_objet, args=['ProfilUtilisateur', profil.id]))
        form = ProfilUtilisateurForm(request.POST, instance=tuteur)
        if form.is_valid():
            tuteur = form.save()
            profil.phone_number = form.cleaned_data['phone_number']
            profil.save()

            if '_reinit' in request.POST and not mail_new_password(request, tuteur):
                return render_to_response('notation/tuteur_form.html', RequestContext(request, {'form' : form, 'bulletins' : bulletins, 'object' : tuteur}))

            return HttpResponseRedirect(reverse('liste_tuteur'))
    else:
        form = ProfilUtilisateurForm(instance=tuteur, initial={'phone_number' : profil.phone_number})
    return render_to_response('notation/tuteur_form.html', RequestContext(request, {'form' : form, 'bulletins' : bulletins, 'object' : tuteur}))


@user_passes_test(lambda u: u.is_authenticated())
def recherche(request):
    search = request.GET.get('search', '')
    if search == '':
        search = 'rien'
    ol = list(Entreprise.objects.filter(nom__istartswith=search))
    ol += list(Bulletin.objects.filter(grille__frm__libelle__istartswith=search))
    # Liste des bulletins qui référencent l'entreprise
    ol += list(Bulletin.objects.filter(entreprise__nom__istartswith=search))
    # Liste des bulletins qui référencent l'eleve
    ol += list(Bulletin.tous.filter(eleve__last_name__istartswith=search))
    ol += list(Bulletin.tous.filter(eleve__first_name__istartswith=search))

    return render_to_response('search.html', RequestContext(request, {'object_list' : ol, 'search_str' : search}))

class SearchMiddleware(object):
    def process_request(self, request):
        if request.method == 'POST' and '_search' in request.POST:
            chaine =  urlquote(request.POST['chaine'])
            return HttpResponseRedirect(reverse('cfai.notation.views.recherche') + '?search=%s' % chaine)
        return None

@user_passes_test(lambda u: u.is_authenticated() and u.get_profile().is_manitou())
def liste_eleve(request):
    grilles = GrilleNotation.objects.all().order_by('frm__libelle', 'promotion')
    object_list = Bulletin.objects.select_related(depth=1)
    if 'id' in request.GET:
        try:
            grille = grilles.get(id=request.GET['id'])
        except:
            grille = grilles[0]
    else:
        grille = grilles[0]
    object_list = object_list.filter(grille__id__exact=grille.id).order_by('eleve__last_name')
    return render_to_response('notation/eleve_list.html', RequestContext(request, {'object_list' : object_list, 'grilles' : grilles, 'gr' : grille}))

@user_passes_test(lambda u: u.is_authenticated() and u.get_profile().is_manitou())
def liste_eleve_supprime(request):
    grilles = GrilleNotation.objects.all().order_by('frm__libelle', 'promotion')
    object_list = Bulletin.supprimes.select_related(depth=1)
    if 'id' in request.GET:
        try:
            grille = grilles.get(id=request.GET['id'])
        except:
            grille = grilles[0]
    else:
        grille = grilles[0]
    object_list = object_list.filter(grille__id__exact=grille.id).order_by('eleve__last_name')
    return render_to_response('notation/eleve_list.html', RequestContext(request, {'object_list' : object_list, 'grilles' : grilles, 'gr' : grille, 'supprime' : True}))

@user_passes_test(lambda u: u.is_authenticated() and u.get_profile().is_manitou())
def liste_bulletin(request):
    grilles = GrilleNotation.objects.all().order_by('frm__libelle', 'promotion')
    object_list = Bulletin.objects.select_related(depth=1)
    if 'id' in request.GET:
        try:
            grille = grilles.get(id=request.GET['id'])
        except:
            grille = grilles[0]
    else:
        grille = grilles[0]
    object_list = object_list.filter(grille__id__exact=grille.id).order_by('grille', 'eleve__last_name')
    return render_to_response('notation/bulletin_list.html', RequestContext(request, {'object_list' : object_list, 'grilles' : grilles, 'gr' : grille}))

@user_passes_test(lambda u: u.is_authenticated() and u.get_profile().is_administratif())
def liste_formation(request):
    if 'id' in request.GET:
        try:
            grille = GrilleNotation.objects.get(id=request.GET['id'])
            grille.archive = not grille.archive
            grille.save()
            messages.success(request, u'Statut de la formation modifié')
        except:
            pass
    grilles = GrilleNotation.objects.all().order_by('frm__libelle', 'promotion')
    return render(request, 'notation/formation_list.html', {'grilles' : grilles})
