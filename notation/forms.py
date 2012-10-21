# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from django.contrib.localflavor.fr.forms import FRPhoneNumberField
from django.forms.util import ErrorList
from cfai.notation.models import *

class SuppressionForm(forms.ModelForm):
    class Meta:
        model = Suppression

class UserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_profile().nom_complet
            
class CreationEleveForm(forms.Form):
    identifiant = forms.CharField(label=u'Nom d\'utilisateur', max_length=30, help_text=u'Lors de la création du compte, un mot de passe aléatoire sera généré.')
    prenom = forms.CharField(label=u'Prénom', max_length=30)
    nom = forms.CharField(label=u'Nom', max_length=30)
    email = forms.EmailField(label=u'Adresse électronique', required=True)
    telephone = FRPhoneNumberField(label=u'N° de téléphone', required=False)
    formation = forms.ModelChoiceField(queryset=GrilleNotation.objects.all())
    entreprise = forms.ModelChoiceField(queryset=Entreprise.objects.all())
    tuteur = UserChoiceField(label=u'Tuteur entreprise', queryset=User.objects.filter(profilutilisateur__user_type='t').order_by('last_name', 'first_name'))
    formateur = UserChoiceField(label=u'Chargé de promotion', queryset=User.objects.filter(profilutilisateur__user_type='f').order_by('last_name', 'first_name'))

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
    email = forms.EmailField(label = u'Adresse électronique', required=True)
    telephone = FRPhoneNumberField(label=u'N° de téléphone', required=False)
    entreprise = forms.ModelChoiceField(queryset=Entreprise.objects.all())
    tuteur = UserChoiceField(label=u'Tuteur entreprise', queryset=User.objects.filter(profilutilisateur__user_type='t').order_by('last_name', 'first_name'))
    formateur = UserChoiceField(label=u'Chargé de promotion', queryset=User.objects.filter(profilutilisateur__user_type='f').order_by('last_name', 'first_name'))

class UtilisateurForm(forms.ModelForm):
    """
    Gère les tuteurs, formateurs et administratifs
    Les champs sont redéfinis afin d'être obligatoires
    """
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')
        
    first_name = forms.CharField(label = u'Prénom', max_length=30)
    last_name = forms.CharField(label = u'Nom', max_length=30)
    email = forms.EmailField(label = u'Adresse électronique')
    phone_number = FRPhoneNumberField(label=u'N° de téléphone', required=False)

class ProfilUtilisateurForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number')

    first_name = forms.CharField(label = u'Prénom', max_length=30, required=True)
    last_name = forms.CharField(label = u'Nom', max_length=30, required=True)
    email = forms.EmailField(label = u'Adresse électronique', required=True)
    phone_number = FRPhoneNumberField(label=u'N° de téléphone', required=False)

class EntrepriseForm(forms.ModelForm):
    class Meta:
        model = Entreprise
    telephone = FRPhoneNumberField(label=u'Téléphone', required=False)
    fax = FRPhoneNumberField(required=False)


class ReadOnly(object):
    def clean(self):
        cleaned_data = self.cleaned_data
        for field in self.fields:
            if self.fields[field].widget.attrs and 'readonly' in self.fields[field].widget.attrs:
                del cleaned_data[field]
        return cleaned_data
    
class NotationForm(forms.Form, ReadOnly):
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
        
        for cap in questions:
            if notes:
                note = notes.filter(capacite=cap)
            else:
                note = None
            self.fields[str(cap.id)] = forms.ChoiceField(label=cap.libelle, choices=APPRECIATIONS, initial=note and note[0].valeur or 'n')
            if profile.is_eleve() or profile.is_formateur():
                self.fields[str(cap.id)].widget.attrs['readonly'] = True

        self.fields['commentaire'] = forms.CharField(widget=forms.Textarea, required=False, initial=commentaire)
        if profile.is_formateur():
            self.fields['commentaire'].widget.attrs['readonly'] = True

class BulletinForm(forms.Form, ReadOnly):
    def __init__(self, *args, **kwargs):
        if 'notes' in kwargs:
            notes = kwargs.pop('notes')
        else:
            notes = None
        user = kwargs.pop('user')
        commentaire = kwargs.pop('commentaire')
        savoirs = kwargs.pop('savoirs')
        profile = user.get_profile()
        super(BulletinForm, self).__init__(*args, **kwargs)

        for sv in savoirs:
            if notes:
                note = notes.filter(savoir=sv)
            else:
                note = None
            self.fields[str(sv.id)] = forms.ChoiceField(label=sv.libelle, choices=NOTES, initial=note and int(note[0].valeur) or 1)
            if profile.is_eleve():
                self.fields[str(sv.id)].widget.attrs['readonly'] = True
            
        self.fields['commentaires_generaux'] = forms.CharField(label=u'Commentaires généraux', widget=forms.Textarea, required=False, initial=commentaire)
        if profile.is_eleve():
            self.fields['commentaires_generaux'].widget.attrs['readonly'] = True
