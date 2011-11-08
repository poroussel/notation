# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import logout
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from cfai.notation.models import *
from cfai.notation.forms import *

@login_required
def index_tuteur(request):
    bulletins = Bulletin.objects.filter(tuteur=request.user)
    return render_to_response('index_tuteur.html', RequestContext(request, {'bulletins' : bulletins}))

@login_required
def index_admin(request):
    return render_to_response('index_admin.html', RequestContext(request))

@login_required
def index_formateur(request):
    bulletins = Bulletin.objects.filter(formateur=request.user)
    return render_to_response('index_formateur.html', RequestContext(request, {'bulletins' : bulletins}))

@login_required
def index_eleve(request):
    bulletins = Bulletin.objects.filter(eleve=request.user)
    return render_to_response('index_eleve.html', RequestContext(request, {'bulletins' : bulletins}))

@login_required
def index(request):
    profile = request.user.get_profile()
    if profile.is_tuteur():
        return HttpResponseRedirect(reverse(index_tuteur))
    if profile.is_administratif():
        return HttpResponseRedirect(reverse(index_admin))
    if profile.is_formateur():
        return HttpResponseRedirect(reverse(index_formateur))
    if profile.is_eleve():
        return HttpResponseRedirect(reverse(index_eleve))
    return render_to_response('index.html', RequestContext(request))

@login_required
def bulletin(request, blt_id):
    blt = get_object_or_404(Bulletin, pk=blt_id)
    # annees = [0, 1, 2] pour une formation de 3 ans
    annees = range(blt.grille.duree)
    ens = EnsembleCapacite.objects.filter(grille=blt.grille)
    return render_to_response('notation/bulletin.html', RequestContext(request, {'bulletin' : blt, 'ens' : ens, 'annees' : annees}))

@login_required
def annee_bulletin(request, blt_id, annee):
    blt = get_object_or_404(Bulletin, pk=blt_id)
    ens = EnsembleCapacite.objects.filter(grille=blt.grille)
    return render_to_response('notation/annee_bulletin.html', RequestContext(request, {'bulletin' : blt, 'annee' : annee, 'ens' : ens}))

@login_required
def ensemble_bulletin(request, blt_id, annee, ens_id):
    blt = get_object_or_404(Bulletin, pk=blt_id)
    ens = get_object_or_404(EnsembleCapacite, pk=ens_id)
    capacites = Capacite.objects.filter(ensemble=ens)
    questions = [(str(x.id), x.libelle, x.cours) for x in capacites if x.valide(annee)]
    # L'utilisation de list() n'est pas nécessaire mais force l'exécution
    # du QuerySet afin déviter une requête imbriquée
    notes = Note.objects.filter(bulletin=blt, capacite__in=list(capacites), annee=annee)

    # Recherche de l'ensemble suivant dans la grille
    # Pourrait être une méthode du modèle
    ensembles = EnsembleCapacite.objects.filter(grille=ens.grille)
    suivant = None
    suivants = ensembles.filter(partie=ens.partie, numero=ens.numero + 1)
    if suivants.count() > 0:
        suivant = suivants[0]
    else:
        suivants = ensembles.filter(partie=chr(ord(ens.partie) + 1), numero=1)
        if suivants.count() > 0:
            suivant = suivants[0]
    precedent = None
    precedents = ensembles.filter(partie=ens.partie, numero=ens.numero - 1)
    if precedents.count() > 0:
        precedent = precedents[0]
    else:
        precedents = ensembles.filter(partie=chr(ord(ens.partie) - 1)).reverse()
        if precedents.count() > 0:
            precedent = precedents[0]

    if request.method == 'POST':
        form = NotationForm(request.POST, questions=questions)
        if form.is_valid():
            for key, value in form.cleaned_data.items():
                cap = Capacite.objects.get(id=int(key))
                if value:
                    note, created = Note.objects.get_or_create(bulletin=blt, capacite=cap, defaults={'valeur' : value, 'annee' : annee, 'auteur_modification' : request.user})
                    if not created:
                        note.valeur = value
                        note.save()
                else:
                    Note.objects.filter(bulletin=blt, capacite=cap).delete()
                    
            if suivant:
                return HttpResponseRedirect(reverse(ensemble_bulletin, args=[blt_id, annee, suivant.id]))
            return HttpResponseRedirect(reverse(bulletin, args=[blt_id]))
    else:
        form = NotationForm(questions=questions, notes=notes)
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
            password_form.save()
            logout(request)
            return HttpResponseRedirect(reverse(index))
    else:
        password_form = PasswordChangeForm(None)
    return render_to_response('notation/utilisateur.html', RequestContext(request, {'password_form' : password_form}))


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
