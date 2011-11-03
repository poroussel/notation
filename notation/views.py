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
    return render_to_response('index_formateur.html', RequestContext(request))

@login_required
def index_eleve(request):
    return render_to_response('index_eleve.html', RequestContext(request))

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
    ens = EnsembleCapacite.objects.filter(grille=blt.grille)
    return render_to_response('notation/bulletin.html', RequestContext(request, {'bulletin' : blt, 'ens' : ens}))

@login_required
def ensemble_bulletin(request, blt_id, ens_id):
    ens = get_object_or_404(EnsembleCapacite, pk=ens_id)
    capacites = Capacite.objects.filter(ensemble=ens)
    return render_to_response('notation/ensemble.html', RequestContext(request, {'ensemble' : ens, 'capacites' : capacites}))

@login_required
def utilisateur(request):
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
            return HttpResponseRedirect(reverse('liste_eleve'))
    else:
        form = CreationEleveForm()
    return render_to_response('notation/eleve_form.html', RequestContext(request, {'form' : form}))

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
    return render_to_response('notation/eleve_form.html', RequestContext(request, {'form' : form}))

@login_required
def ajouter_tuteur(request):
    if request.method == 'POST':
        form = UtilisateurForm(request.POST)
    else:
        form = UtilisateurForm()
    return render_to_response('notation/tuteur_form.html', RequestContext(request, {'form' : form}))

@login_required
def ajouter_formateur(request):
    if request.method == 'POST':
        form = UtilisateurForm(request.POST)
    else:
        form = UtilisateurForm()
    return render_to_response('notation/formateur_form.html', RequestContext(request, {'form' : form}))
