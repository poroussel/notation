# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from notation.models import *
from django.contrib.localflavor.fr.forms import FRPhoneNumberField

class UserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name()
            
class AjouterEleveForm(forms.Form):
    identifiant = forms.CharField(max_length=30)
    prenom = forms.CharField(label = u'Prénom', max_length=30)
    nom = forms.CharField(label = u'Nom', max_length=30)
    email = forms.EmailField(label = u'Adresse email', required=False)
    formation = forms.ModelChoiceField(queryset=GrilleNotation.objects.all())
    entreprise = forms.ModelChoiceField(queryset=Entreprise.objects.all())
    tuteur = UserChoiceField(queryset=User.objects.filter(profilutilisateur__user_type='t'))
    formateur = UserChoiceField(queryset=User.objects.filter(profilutilisateur__user_type='f'))
    
class EntrepriseForm(forms.ModelForm):
    class Meta:
        model = Entreprise
    telephone = FRPhoneNumberField(label=u'Téléphone', required=False)
    fax = FRPhoneNumberField(required=False)
