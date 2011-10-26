# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User


class GrilleNotation(models.Model):
    """
    Une grille de notation existe pour une formation et une promotion
    """
    class Meta:
        verbose_name = u'Grille de notation'
        verbose_name_plural = u'Grilles de notation'
        
    formation = models.CharField(u'Nom de la formation', max_length=100, blank=False)
    promotion = models.PositiveIntegerField(u'Première années de la promotion')
    duree = models.PositiveIntegerField(u'Durée en années de la formation')

class Entreprise(models.Model):
    nom = models.CharField(u'Nom', max_length=80)
    description = models.TextField(u'Description', blank=True)

    def __unicode__(self):
        return self.nom
    
class Eleve(models.Model):
    """
    Un élève est encadré par un tuteur, supervisé par un formateur et
    lié à une grille de notation et une entreprise.
    
    Dans le cas d'un même élève participant à plusieurs formations, les
    champs devront être écrasés et l'historique sera perdu.
    """
    class Meta:
        verbose_name = u'Elève'
        verbose_name_plural = u'Elèves'
        
    nom = models.CharField(u'Nom', max_length=80)
    prenom = models.CharField(u'Prénom', max_length=80)
    grille = models.ForeignKey(GrilleNotation, verbose_name=u'Formation suivie')
    entreprise = models.ForeignKey(Entreprise)
    tuteur = models.ForeignKey(User, related_name='tuteur', verbose_name=u'Tuteur')
    formateur = models.ForeignKey(User, related_name='formateur', verbose_name='Formateur')

    def __unicode__(self):
        return u'%s %s' % (self.prenom, self.nom)

class CommentaireCompetence(models.Model):
    """
    Permet le stockage d'un commentaire libre pour un élève et un
    ensemble de compétences
    
    Doit être modifiable par l'élève ce qui nécessite un login/password pour les élèves
    """
    class Meta:
        verbose_name = u'Commentaire sur un ensemble de compétences'
        verbose_name_plural = u'Commentaires sur des ensembles de compétences'
        
    eleve = models.ForeignKey(Eleve)

class Competence(models.Model):
    """
    """
    class Meta:
        verbose_name = u'Compétence'
        verbose_name_plural = u'Compétences'
        

class Note(models.Model):
    """
    Relie une note à un élève et à une compétence
    L'année est une donnée
    """
    valeur = models.DecimalField(max_digits=3, decimal_places=1)
    competence = models.ForeignKey(Competence)
    # FIXME : est-ce un numero (1, 2, 3) ou une annee ?
    annee = models.PositiveIntegerField(u'Année')

class EnsembleCompetence(models.Model):
    """
    """
    class Meta:
        verbose_name = u'Ensemble de compétences'
        verbose_name_plural = u'Ensembles de compétences'

