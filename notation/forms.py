# -*- coding: utf-8 -*-

from django import forms
from django.db.models import Q
from notation.models import *

class AjouterEleveForm(forms.Form):
    prenom = forms.CharField(label = u'Prénom', max_length=80)
    nom = forms.CharField(label = u'Nom', max_length=80)
    email = forms.EmailField(label = u'Adresse email', required=False)
