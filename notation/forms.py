# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from django.contrib.localflavor.fr.forms import FRPhoneNumberField
from django.forms.util import ErrorList
from notation.models import *

class UserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name()
            
class CreationEleveForm(forms.Form):
    identifiant = forms.CharField(label=u'Nom d\'utilisateur', max_length=30, help_text=u'Lors de la création du compte, le mot de passe sera initialisé avec la même valeur.')
    prenom = forms.CharField(label=u'Prénom', max_length=30)
    nom = forms.CharField(label=u'Nom', max_length=30)
    email = forms.EmailField(label=u'Adresse email', required=True)
    formation = forms.ModelChoiceField(queryset=GrilleNotation.objects.all())
    entreprise = forms.ModelChoiceField(queryset=Entreprise.objects.all())
    tuteur = UserChoiceField(label=u'Tuteur entreprise', queryset=User.objects.filter(profilutilisateur__user_type='t'))
    formateur = UserChoiceField(label=u'Chargé de promotion', queryset=User.objects.filter(profilutilisateur__user_type='f'))

    def clean(self):
      """
      L'identifiant ne doit pas déjà exister dans la base.
      """
      cd = self.cleaned_data
      if 'identifiant' in cd:
          if User.objects.filter(username=cd['identifiant']).exists():
              self._errors['identifiant'] = ErrorList(['Un(e) Utilisateur avec ce Nom d\'utilisateur existe déjà.'])
              del cd['identifiant']
      return cd

class EditionEleveForm(forms.Form):
    prenom = forms.CharField(label = u'Prénom', max_length=30)
    nom = forms.CharField(label = u'Nom', max_length=30)
    email = forms.EmailField(label = u'Adresse email', required=True)
    entreprise = forms.ModelChoiceField(queryset=Entreprise.objects.all())
    tuteur = UserChoiceField(label=u'Tuteur entreprise', queryset=User.objects.filter(profilutilisateur__user_type='t'))
    formateur = UserChoiceField(label=u'Chargé de promotion', queryset=User.objects.filter(profilutilisateur__user_type='f'))

class UtilisateurForm(forms.ModelForm):
    """
    Gère les tuteurs, formateurs et administratifs
    Les champs sont redéfinis afin d'être obligatoires
    """
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        
    first_name = forms.CharField(label = u'Prénom', max_length=30)
    last_name = forms.CharField(label = u'Nom', max_length=30)
    email = forms.EmailField(label = u'Adresse électronique')

class EntrepriseForm(forms.ModelForm):
    class Meta:
        model = Entreprise
    telephone = FRPhoneNumberField(label=u'Téléphone', required=False)
    fax = FRPhoneNumberField(required=False)


class NotationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        if 'notes' in kwargs:
            notes = kwargs.pop('notes')
        else:
            notes = None
        if 'commentaire' in kwargs:
            commentaire = kwargs.pop('commentaire')
        else:
            commentaire = None
        questions = kwargs.pop('questions')
        user = kwargs.pop('user')
        profile = user.get_profile()
        super(NotationForm, self).__init__(*args, **kwargs)
        
        for id,question,cours in questions:
            if notes:
                note = notes.filter(capacite__id=id)
            else:
                note = None
            self.fields[str(id)] = forms.IntegerField(label=question, help_text=cours and u'Cours associé : %s' % cours or None, min_value=0, max_value=5, required=False, initial=note and int(note[0].valeur) or None)
            if profile.is_eleve() or profile.is_formateur():
                self.fields[str(id)].widget.attrs['disabled'] = True

        self.fields['commentaire'] = forms.CharField(widget=forms.Textarea, required=False, initial=commentaire)
        if profile.is_formateur():
            self.fields['commentaire'].widget.attrs['disabled'] = True
        
