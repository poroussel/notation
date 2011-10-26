# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, Http404
from cfai.notation.models import *


@login_required
def index(request):
    return render_to_response('index.html', RequestContext(request))
