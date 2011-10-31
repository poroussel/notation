# -*- coding: utf-8 -*-

from django import forms
from notation.models import *
from django.contrib.localflavor.fr.forms import FRPhoneNumberField

class AjouterEleveForm(forms.Form):
    prenom = forms.CharField(label = u'Prénom', max_length=80)
    nom = forms.CharField(label = u'Nom', max_length=80)
    email = forms.EmailField(label = u'Adresse email', required=False)

class EntrepriseForm(forms.ModelForm):
    class Meta:
        model = Entreprise
    telephone = FRPhoneNumberField(label=u'Téléphone', required=False)
    fax = FRPhoneNumberField(required=False)
