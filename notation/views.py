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
def bulletin(request, object_id):
    blt = get_object_or_404(Bulletin, pk=object_id)
    ens = EnsembleCapacite.objects.filter(grille=blt.grille)
    return render_to_response('notation/bulletin.html', RequestContext(request, {'bulletin' : blt, 'ens' : ens}))

@login_required
def ensemble(request, object_id):
    ens = get_object_or_404(EnsembleCapacite, pk=object_id)
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
    form = AjouterEleveForm()
    return render_to_response('notation/ajouter_eleve.html', RequestContext(request, {'form' : form}))
@login_required
def ajouter_tuteur(request):
    pass
@login_required
def ajouter_formateur(request):
    pass
