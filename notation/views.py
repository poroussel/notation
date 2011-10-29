# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from cfai.notation.models import *

@login_required
def index_tuteur(request):
    bulletins = Bulletin.objects.filter(tuteur=request.user)
    return render_to_response('index_tuteur.html', RequestContext(request, {'bulletins' : bulletins}))

@login_required
def index(request):
    if request.user.get_profile().is_tuteur():
        return HttpResponseRedirect(reverse(index_tuteur))
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
    password_form = PasswordChangeForm(request.user)
    return render_to_response('notation/utilisateur.html', RequestContext(request, {'password_form' : password_form}))

