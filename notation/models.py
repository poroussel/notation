# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.conf import settings

TYPES = (('e', u'Apprenti'),
         ('t', u'Tuteur entreprise'),
         ('f', u'Chargé de promotion'),
         ('a', u'Administratif'))

class ProfilUtilisateur(models.Model):
    user = models.OneToOneField(User, unique=True)
    user_type = models.CharField(u'Type', max_length=1, default='e', choices=TYPES)

    def __unicode__(self):
        return u'%s - %s' % (self.nom_complet, self.get_user_type_display())

    def is_tuteur(self):
        return self.user_type == 't'
    def is_eleve(self):
        return self.user_type == 'e'
    def is_formateur(self):
        return self.user_type == 'f'
    def is_administratif(self):
        return self.user_type == 'a'

    def _nom_complet(self):
        return '%s %s' % (self.user.first_name, self.user.last_name)
    nom_complet = property(_nom_complet)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = ProfilUtilisateur.objects.get_or_create(user=instance)
        if settings.DEBUG:
            print u"Création de l'utilisateur %s et envoi d'un email à l'adresse %s" % (instance.username, instance.email)
post_save.connect(create_user_profile, sender=User)


class GrilleNotation(models.Model):
    """
    Une grille de notation existe pour une formation et une promotion.
    Chaque élève est lié à une et une seule grille.
    """
    class Meta:
        verbose_name = u'Grille de notation'
        verbose_name_plural = u'Grilles de notation'
        
    formation = models.CharField(u'Nom de la formation', max_length=100, blank=False)
    promotion = models.PositiveIntegerField(u'Première année de la promotion')
    duree = models.PositiveIntegerField(u'Durée en années de la formation')
    poids_capacite = models.PositiveIntegerField(u'Poids de la moyenne des capacités dans la moyenne générale', default=1)
    poids_savoir_etre = models.PositiveIntegerField(u'Poids de la moyenne des savoirs être dans la moyenne générale', default=1)

    def __unicode__(self):
        return u'%s / %d - %d' % (self.formation, self.promotion, self.promotion + self.duree - 1)

class Entreprise(models.Model):
    nom = models.CharField(u'Nom', max_length=80)
    description = models.TextField(u'Description', blank=True)
    telephone = models.CharField(u'Téléphone', max_length=15, blank=True)
    fax = models.CharField(max_length=15, blank=True)
    
    def __unicode__(self):
        return self.nom

    @models.permalink
    def get_absolute_url(self):
        return ('detail_entreprise', [self.id])
        
    
class Bulletin(models.Model):
    """
    Bulletin de notes d'un élève pour une formation
    """
    class Meta:
        verbose_name = u'Bulletin'
        verbose_name_plural = u'Bulletins'
        
    eleve = models.ForeignKey(User, related_name='eleve', verbose_name=u'Apprenti')
    grille = models.ForeignKey(GrilleNotation, verbose_name=u'Formation suivie')
    entreprise = models.ForeignKey(Entreprise)
    tuteur = models.ForeignKey(User, related_name='tuteur', verbose_name=u'Tuteur entreprise')
    formateur = models.ForeignKey(User, related_name='formateur', verbose_name=u'Tuteur académique')

    def __unicode__(self):
        return u'Bulletin de %s (%s - %s)' % (self.eleve.get_full_name(), self.grille, self.entreprise)

    @models.permalink
    def get_absolute_url(self):
        return ('bulletin', [self.id])


class EnsembleCapacite(models.Model):
    """
    """
    class Meta:
        verbose_name = u'Ensemble de capacités'
        verbose_name_plural = u'Ensembles de capacités'
        order_with_respect_to = 'grille'
        ordering = ['partie', 'numero']
        unique_together = ('grille', 'partie', 'numero')

    grille = models.ForeignKey(GrilleNotation)
    # Relie plusieurs ensembles dans une catégorie
    partie = models.CharField(max_length=1)
    numero = models.PositiveIntegerField()
    libelle = models.CharField(u'Libellé', max_length=80)
    poids = models.PositiveIntegerField(default=1)

    def precedent(self):
        precedents = EnsembleCapacite.objects.filter(grille=self.grille, partie=self.partie, numero=self.numero - 1)
        if precedents.count() > 0:
            return precedents[0]
        precedents = EnsembleCapacite.objects.filter(grille=self.grille, partie=chr(ord(self.partie) - 1)).reverse()
        if precedents.count() > 0:
            return precedents[0]
        return None
    
    def suivant(self):
        suivants = EnsembleCapacite.objects.filter(grille=self.grille, partie=self.partie, numero=self.numero + 1)
        if suivants.count() > 0:
            return suivants[0]
        suivants = EnsembleCapacite.objects.filter(grille=self.grille, partie=chr(ord(self.partie) + 1), numero=1)
        if suivants.count() > 0:
            return suivants[0]
        return None
    
    def __unicode__(self):
        return u'%c.%d %s'% (self.partie, self.numero, self.libelle)

class Capacite(models.Model):
    """
    """
    class Meta:
        verbose_name = u'Capacité'
        verbose_name_plural = u'Capacités'
        # FIXME : pas sur que les lignes suivantes servent à qq chose
        order_with_respect_to = 'ensemble'
        ordering = ['numero']
        unique_together = ('ensemble', 'numero')

    ensemble = models.ForeignKey(EnsembleCapacite)
    numero = models.PositiveIntegerField()
    libelle = models.CharField(u'Libellé', max_length=80)
    cours = models.CharField(u'Cours associé', max_length=80, blank=True)
    an_1 = models.BooleanField(u'Valide pour la première année')
    an_2 = models.BooleanField(u'Valide pour la deuxième année')
    an_3 = models.BooleanField(u'Valide pour la troisième année')

    def valide(self, annee):
        if int(annee) < self.ensemble.grille.duree:
            return self.__dict__['an_%d' % (int(annee) + 1)]
        return False
        
    def __unicode__(self):
        return u'%c.%d.%d %s'% (self.ensemble.partie, self.ensemble.numero, self.numero, self.libelle)

class Note(models.Model):
    """
    """
    bulletin = models.ForeignKey(Bulletin)
    capacite = models.ForeignKey(Capacite)
    valeur = models.DecimalField(max_digits=3, decimal_places=1)
    # Indice dans la liste des annees (0, 1 etc) 
    annee = models.PositiveIntegerField(u'Année')
    date_modification = models.DateTimeField(auto_now=True)
    auteur_modification = models.ForeignKey(User)
    
    def eleve(self):
        """
        Méthode utilisée dans le vue liste admin
        """
        return self.bulletin.eleve.get_full_name()
    
    def __unicode__(self):
        return u'Note de %s pour la capacité %s'% (self.bulletin.eleve.get_full_name(), self.capacite)

class Commentaire(models.Model):
    """
    Permet le stockage d'un commentaire libre pour un bulletin et un
    ensemble de capacités
    
    Doit être modifiable par l'élève ce qui nécessite un login/password pour les élèves
    """
    class Meta:
        verbose_name = u'Commentaire'
        verbose_name_plural = u'Commentaires'
        
    bulletin = models.ForeignKey(Bulletin)
    ensemble = models.ForeignKey(EnsembleCapacite)
    texte = models.TextField()
    date_modification = models.DateTimeField(auto_now=True)
    auteur_modification = models.ForeignKey(User)

    def eleve(self):
        """
        Méthode utilisée dans le vue liste admin
        """
        return self.bulletin.eleve.get_full_name()

    def __unicode__(self):
        return u'Commentaire de %s pour le groupe %s'% (self.bulletin.eleve.get_full_name(), self.ensemble)
