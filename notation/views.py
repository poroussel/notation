# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
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
from django.db.models import Count
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from cfai.notation.models import *
from cfai.notation.forms import *
from cfai.notation.excel import *

@login_required
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

@user_passes_test(lambda u: u.is_authenticated() and u.get_profile().is_manitou())
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
    if profile.is_manitou():
        return HttpResponseRedirect(reverse(index_admin))
    if profile.is_formateur():
        return HttpResponseRedirect(reverse(index_formateur))
    if profile.is_eleve():
        return HttpResponseRedirect(reverse(index_eleve))
    return render_to_response('index.html', RequestContext(request))

@login_required
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

@login_required
def bulletin(request, blt_id):
    blt = get_object_or_404(Bulletin, pk=blt_id)
    if request.GET.get('format', None) == 'xls':
        return bulletin_xls(request, blt)
    annees = range(blt.grille.duree)
    return render_to_response('notation/bulletin.html', RequestContext(request, {'bulletin' : blt, 'annees' : annees}))

@user_passes_test(lambda u: u.is_authenticated() and (u.get_profile().is_manitou() or u.get_profile().is_tuteur() or u.get_profile().is_eleve()))
def annee_bulletin(request, blt_id, annee):
    """
    Affiche la liste des ensembles de capacités d'un bulletin
    pour une annnée, le formulaire de saisie des savoirs être
    ainsi que les moyennes actuelles pour l'année.
    """
    blt = get_object_or_404(Bulletin, pk=blt_id)
    ens = blt.grille.ensemblecapacite_set.filter(capacite__code_annee__contains=annee).annotate(nbre_capacite=Count('capacite'))
    setre = blt.grille.savoiretre_set.filter(code_annee__contains=annee)
    notes = Note.objects.filter(bulletin=blt, savoir__in=list(setre), annee=annee)
    moyenne = Moyenne.objects.filter(annee=annee, bulletin=blt)
    
    form = BulletinForm(commentaire=blt.commentaires_generaux, notes=notes, savoirs=setre, user=request.user)
    if request.method == 'POST':
        form = BulletinForm(request.POST, commentaire=blt.commentaires_generaux, savoirs=setre, user=request.user)
        if form.is_valid():
            if 'commentaires_generaux' in form.cleaned_data:
                blt.commentaires_generaux = form.cleaned_data['commentaires_generaux']
                blt.save()

            for sv in setre:
                if str(sv.id) in form.cleaned_data:
                    value = form.cleaned_data[str(sv.id)]
                    if value:
                        note, created = Note.objects.get_or_create(bulletin=blt, savoir=sv, annee=annee, defaults={'valeur' : value, 'auteur_modification' : request.user})
                        if not created:
                            note.valeur = value
                            note.auteur_modification = request.user
                            note.save()
                    else:
                        Note.objects.filter(bulletin=blt, savoir=sv, annee=annee).delete()
            blt.calcul_moyenne_savoir(annee, request.user)
    return render_to_response('notation/annee_bulletin.html', RequestContext(request, {'bulletin' : blt, 'annee' : annee, 'ens' : ens, 'form' : form, 'moyenne' : moyenne}))

@user_passes_test(lambda u: u.is_authenticated() and (u.get_profile().is_manitou() or u.get_profile().is_tuteur() or u.get_profile().is_eleve()))
def ensemble_bulletin(request, blt_id, annee, ens_id):
    blt = get_object_or_404(Bulletin, pk=blt_id)
    ens = get_object_or_404(EnsembleCapacite, pk=ens_id)
    capacites = ens.capacite_set.filter(code_annee__contains=annee)
    notes = Note.objects.filter(bulletin=blt, capacite__in=list(capacites), annee=annee)
    
    commentaires = Commentaire.objects.filter(bulletin=blt, ensemble=ens)
    commentaire = commentaires and commentaires[0].texte or None

    suivant = ens.suivant()
    while suivant and not suivant.capacite_set.filter(code_annee__contains=annee):
        suivant = suivant.suivant()
    precedent = ens.precedent()
    while precedent and not precedent.capacite_set.filter(code_annee__contains=annee):
        precedent = precedent.precedent()

    if request.method == 'POST':
        form = NotationForm(request.POST, questions=capacites, user=request.user)
        if form.is_valid():
            if 'commentaire' in form.cleaned_data:
                com, created = Commentaire.objects.get_or_create(bulletin=blt, ensemble=ens, defaults={'texte' : form.cleaned_data['commentaire'], 'auteur_modification' : request.user})
                if not created:
                    com.texte = form.cleaned_data['commentaire']
                    com.save()
                        
            for cap in capacites:
                if str(cap.id) in form.cleaned_data:
                    value = form.cleaned_data[str(cap.id)]
                    if value:
                        note, created = Note.objects.get_or_create(bulletin=blt, capacite=cap, annee=annee, defaults={'valeur' : value, 'auteur_modification' : request.user})
                        if not created:
                            note.valeur = value
                            note.auteur_modification = request.user
                            note.save()
                    else:
                        Note.objects.filter(bulletin=blt, capacite=cap, annee=annee).delete()

            blt.calcul_moyenne_competence(annee, request.user)
            if suivant:
                return HttpResponseRedirect(reverse(ensemble_bulletin, args=[blt_id, annee, suivant.id]))
            return HttpResponseRedirect(reverse(bulletin, args=[blt_id]))
    else:
        form = NotationForm(questions=capacites, notes=notes, commentaire=commentaire, user=request.user)
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

def mail_new_user(request, user):
    body = render_to_string('creation_compte.txt', {'profil' : user.get_profile(), 'site' : Site.objects.get_current()})
    try:
        eleve.email_user(u'[CFAI/ENSMM] Création de votre compte', body, from_email=settings.SERVER_EMAIL)
        messages.success(request, u'Un email a été envoyé à %s.' % user.get_full_name())
    except:
        messages.error(request, u'Une erreur s\'est produite lors de l\'envoi d\'un email à %s, veuillez vérifier l\'adresse.' % user.email)
        return False
    return True

@login_required
def ajouter_eleve(request):
    if request.method == 'POST':
        form = CreationEleveForm(request.POST)
        if form.is_valid():
            eleve = User()
            eleve.username = form.cleaned_data['identifiant']
            eleve.password = User.objects.make_random_password()
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

            if not mail_new_user(request, eleve):
                return HttpResponseRedirect(reverse('detail_eleve', args=[eleve.id]))

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
    profil = elv.get_profile()
    blt = Bulletin.objects.get(eleve=elv)
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

            
            if '_reinit' in request.POST:
                elv.password = User.objects.make_random_password()
                elv.save()
                body = render_to_string('creation_compte.txt', {'profil' : elv.get_profile(), 'site' : Site.objects.get_current()})
                try:
                    elv.email_user(u'[CFAI/ENSMM] Réinitialisation de votre compte', body, from_email=settings.SERVER_EMAIL)
                    messages.success(request, u'Un email a été envoyé à %s.' % elv.get_full_name())
                except:
                    messages.error(request, u'Une erreur s\'est produite lors de l\'envoi d\'un email à %s, veuillez vérifier l\'adresse.' % elv.email)
                    return render_to_response('notation/eleve_form.html', RequestContext(request, {'form' : form, 'blt' : blt}))
                
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
    return render_to_response('notation/eleve_form.html', RequestContext(request, {'form' : form, 'blt' : blt, 'object' : elv}))

@user_passes_test(lambda u: u.is_authenticated() and u.get_profile().is_administratif())
def ajouter_tuteur(request):
    if request.method == 'POST':
        form = UtilisateurForm(request.POST)
        if form.is_valid():
            tuteur = form.save()
            tuteur.password = User.objects.make_random_password()
            tuteur.save()
            profil = ProfilUtilisateur.objects.get(user=tuteur)
            profil.user_type = 't'
            profil.phone_number = form.cleaned_data['phone_number']
            profil.save()

            if not mail_new_user(request, tuteur):
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
            formateur.password = User.objects.make_random_password()
            formateur.save()
            profil = ProfilUtilisateur.objects.get(user=formateur)
            profil.user_type = 'f'
            profil.phone_number = form.cleaned_data['phone_number']
            profil.save()

            if not mail_new_user(request, tuteur):
                return HttpResponseRedirect(reverse('detail_formateur', args=[formateur.id]))

            if '_continuer' in request.POST:
                return HttpResponseRedirect(reverse('ajouter_formateur'))
            return HttpResponseRedirect(reverse('liste_formateur'))
    else:
        form = UtilisateurForm()
    return render_to_response('notation/formateur_form.html', RequestContext(request, {'form' : form}))

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
        form = ProfilUtilisateurForm(request.POST, instance=frm)
        if form.is_valid():
            formateur = form.save()
            profil.phone_number = form.cleaned_data['phone_number']
            profil.save()
            
            if '_reinit' in request.POST:
                formateur.password = User.objects.make_random_password()
                formateur.save()
                body = render_to_string('creation_compte.txt', {'profil' : formateur.get_profile(), 'site' : Site.objects.get_current()})
                try:
                    formateur.email_user(u'[CFAI/ENSMM] Réinitialisation de votre compte', body, from_email=settings.SERVER_EMAIL)
                    messages.success(request, u'Un email a été envoyé à %s.' % formateur.get_full_name())
                except:
                    messages.error(request, u'Une erreur s\'est produite lors de l\'envoi d\'un email à %s, veuillez vérifier l\'adresse.' % formateur.email)
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
        form = ProfilUtilisateurForm(request.POST, instance=tuteur)
        if form.is_valid():
            tuteur = form.save()
            profil.phone_number = form.cleaned_data['phone_number']
            profil.save()
            
            if '_reinit' in request.POST:
                tuteur.password = User.objects.make_random_password()
                tuteur.save()
                body = render_to_string('creation_compte.txt', {'profil' : tuteur.get_profile(), 'site' : Site.objects.get_current()})
                try:
                    tuteur.email_user(u'[CFAI/ENSMM] Réinitialisation de votre compte', body, from_email=settings.SERVER_EMAIL)
                    messages.success(request, u'Un email a été envoyé à %s.' % tuteur.get_full_name())
                except:
                    messages.error(request, u'Une erreur s\'est produite lors de l\'envoi d\'un email à %s, veuillez vérifier l\'adresse.' % tuteur.email)
                    return render_to_response('notation/tuteur_form.html', RequestContext(request, {'form' : form, 'bulletins' : bulletins, 'object' : tuteur}))
                
            return HttpResponseRedirect(reverse('liste_tuteur'))
    else:
        form = ProfilUtilisateurForm(instance=tuteur, initial={'phone_number' : profil.phone_number})
    return render_to_response('notation/tuteur_form.html', RequestContext(request, {'form' : form, 'bulletins' : bulletins, 'object' : tuteur}))


@user_passes_test(lambda u: u.is_authenticated() and u.get_profile().is_administratif())
def recherche(request):
    search = request.GET.get('search', '')
    if search == '':
        search = 'rien'
    ol = list(Entreprise.objects.filter(nom__istartswith=search))
    ol += list(Bulletin.objects.filter(grille__frm__libelle__istartswith=search))
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
