# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from datetime import date

TYPES = (('e', u'Apprenti'),
         ('t', u'Tuteur entreprise'),
         ('f', u'Chargé de promotion'),
         ('a', u'Administratif'))

NOMS_ANNEES = [u'1ère année', u'2ème année', u'3ème année']

class ProfilUtilisateur(models.Model):
    user = models.OneToOneField(User, unique=True)
    user_type = models.CharField(u'Type', max_length=1, default='e', choices=TYPES)
    password_modified = models.BooleanField(default=False, editable=True)
    phone_number = models.CharField(u'N° de téléphone', max_length=15, blank=True)
                                            
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
        profil, created = ProfilUtilisateur.objects.get_or_create(user=instance)
        if settings.DEBUG:
            print u"Création de l'utilisateur %s et envoi d'un email à l'adresse %s" % (instance.username, instance.email)
        current_site = Site.objects.get_current()
        body = render_to_string('creation_compte.txt', {'profil' : profil, 'site' : current_site})
        print body
        send_mail(u'Création de votre compte', body, 'admnistrateur@%s' % current_site.domain, list(instance.email), fail_silently=True)
post_save.connect(create_user_profile, sender=User)


class Formation(models.Model):
    libelle = models.CharField(u'Libellé', max_length=80)
    duree = models.PositiveIntegerField(u'Durée en années de la formation')

    def __unicode__(self):
        return self.libelle

class GrilleNotation(models.Model):
    """
    Une grille de notation existe pour une formation et une promotion.
    Chaque eleve est lie a une et une seule grille.
    """
    class Meta:
        verbose_name = u'Grille de notation'
        verbose_name_plural = u'Grilles de notation'
        ordering = ['frm', '-promotion']

    frm = models.ForeignKey(Formation, verbose_name='Formation')
    promotion = models.PositiveIntegerField(u'Première année de la promotion')
    duree = models.PositiveIntegerField(u'Durée en années de la formation')
    poids_capacite = models.PositiveIntegerField(u'Poids de la moyenne des capacités dans la moyenne générale', default=1)
    poids_savoir_etre = models.PositiveIntegerField(u'Poids de la moyenne des savoirs être dans la moyenne générale', default=1)

    def __unicode__(self):
        return u'%s / %d - %d' % (self.frm.libelle, self.promotion, self.promotion + self.duree - 1)

    def annee_promotion_courante(self):
        """
        Retourne l'annee en cours de la promotion (0, 1, 2) pour la date
        du jour. Les années scolaires vont de septembre à août.

        Retourne -1 si la date est en dehors de la promotion.
        """
        ajd = date.today()
        for inc in range(0, self.duree):
            debut_annee = date(self.promotion + inc, 9, 1)
            fin_annee = date(self.promotion + inc + 1, 8, 30)
            if debut_annee <= ajd and ajd <= fin_annee:
                return inc
        return -1

    def nom_promotion_courante(self):
        annee = self.annee_promotion_courante()
        if annee == -1:
            return None
        return NOMS_ANNEES[annee]

def maj_bulletins_de_grille(sender, instance, created, **kwargs):
    """
    Lorsqu'une grille est modifiee les moyennes des bulletins associes
    doivent etre recalculees pour prendre en compte la modification
    eventuelle des poids.
    """
    if not created:
        moyennes = Moyenne.objects.filter(bulletin__grille=instance)
        for moyenne in moyennes:
            moyenne.save()
post_save.connect(maj_bulletins_de_grille, sender=GrilleNotation)


class Entreprise(models.Model):
    nom = models.CharField(u'Nom', max_length=80)
    description = models.TextField(u'Description', blank=True)
    telephone = models.CharField(u'N° de téléphone', max_length=15, blank=True)
    fax = models.CharField(u'N° de fax', max_length=15, blank=True)
    
    def __unicode__(self):
        return self.nom

    @models.permalink
    def get_absolute_url(self):
        return ('detail_entreprise', [self.id])
        
    
class Bulletin(models.Model):
    """
    Bulletin de notes d'un eleve pour une formation

    Il serait preferable point de vue structure et acces
    aux donnees de stocker un bulletin par annee. Cela
    permettrait d'acceder aux notes et aux moyennes tres
    facilement.
    """
    class Meta:
        verbose_name = u'Bulletin'
        verbose_name_plural = u'Bulletins'
        
    eleve = models.ForeignKey(User, related_name='eleve', verbose_name=u'Apprenti')
    grille = models.ForeignKey(GrilleNotation, verbose_name=u'Formation suivie')
    entreprise = models.ForeignKey(Entreprise)
    tuteur = models.ForeignKey(User, related_name='tuteur', verbose_name=u'Tuteur entreprise')
    formateur = models.ForeignKey(User, related_name='formateur', verbose_name=u'Tuteur académique')
    commentaires_generaux = models.TextField(u'Commentaires généraux')
    date_modification = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'Bulletin de %s (%s - %s)' % (self.eleve.get_full_name(), self.grille, self.entreprise)

    @models.permalink
    def get_absolute_url(self):
        return ('bulletin', [self.id])

    def moyenne_ensemble(self, ens, annee):
        """
        Calcul de la moyenne pour un ensemble de capacités pour une année.
        Les notes manquantes (non saisies) sont considérées comme valant 1
        """
        capacites = [cap for cap in ens.capacite_set.all() if cap.valide(annee)]
        if len(capacites) == 0:
            return None
        notes = Note.objects.filter(bulletin=self, annee=annee, capacite__in=capacites).values_list('valeur', flat=True)
        somme = sum(notes)
        somme += len(capacites) - len(notes)
        return somme / len(capacites)

    def calcul_moyenne_competence(self, annee):
        """
        Calcul la moyenne compétence de ce bulletin pour une année
        """
        annee = int(annee)
        total = 0
        poids = 0
        ensembles = self.grille.ensemblecapacite_set.all()
        for ens in ensembles:
            moyenne_ensemble = self.moyenne_ensemble(ens, annee)
            if moyenne_ensemble:
                total += moyenne_ensemble * ens.poids
                poids += ens.poids
        moyenne = total * 4 / poids
        moy, created = Moyenne.objects.get_or_create(bulletin=self, annee=annee, defaults={'valeur_cp' : moyenne})
        if not created:
            moy.valeur_cp = moyenne
            moy.save()

    def calcul_moyenne_savoir(self, annee):
        """
        Calcul la moyenne savoir être de ce bulletin pour une année
        """
        annee = int(annee)
        savoirs = [sv for sv in self.grille.savoiretre_set.all() if sv.valide(annee)]

        notes = Note.objects.filter(bulletin=self, annee=annee, savoir__in=savoirs).values_list('valeur', flat=True)
        somme = sum(notes)
        somme += len(savoirs) - len(notes)
        moyenne = somme / len(savoirs)

        moy, created = Moyenne.objects.get_or_create(bulletin=self, annee=annee, defaults={'valeur_sv' : moyenne})
        if not created:
            moy.valeur_sv = moyenne
            moy.save()

class EnsembleCapacite(models.Model):
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
    libelle = models.CharField(u'Libellé', max_length=200)
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
    class Meta:
        verbose_name = u'Capacité'
        verbose_name_plural = u'Capacités'
        # FIXME : pas sur que les lignes suivantes servent à qq chose
        order_with_respect_to = 'ensemble'
        ordering = ['numero']
        unique_together = ('ensemble', 'numero')

    ensemble = models.ForeignKey(EnsembleCapacite)
    numero = models.PositiveIntegerField()
    libelle = models.CharField(u'Libellé', max_length=200)
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

class SavoirEtre(models.Model):
    class Meta:
        verbose_name = u'Savoir être'
        verbose_name_plural = u'Savoirs être'

    grille = models.ForeignKey(GrilleNotation)
    libelle = models.CharField(u'Libellé', max_length=200)
    an_1 = models.BooleanField(u'Valide pour la première année')
    an_2 = models.BooleanField(u'Valide pour la deuxième année')
    an_3 = models.BooleanField(u'Valide pour la troisième année')

    def valide(self, annee):
        if int(annee) < self.grille.duree:
            return self.__dict__['an_%d' % (int(annee) + 1)]
        return False
        
    def __unicode__(self):
        return self.libelle

class Moyenne(models.Model):
    class Meta:
        ordering = ['annee']
        
    bulletin = models.ForeignKey(Bulletin)
    annee = models.PositiveIntegerField()
    valeur_cp = models.DecimalField(u'Moyenne compétence', max_digits=4, decimal_places=2, default=0)
    valeur_sv = models.DecimalField(u'Moyenne savoir être', max_digits=4, decimal_places=2, default=0)
    valeur_gn = models.DecimalField(u'Moyenne générale', max_digits=4, decimal_places=2, default=0)

    def __unicode__(self):
        return u'Moyenne de %s pour la %s' % (self.bulletin.eleve.get_full_name(), NOMS_ANNEES[self.annee])

def maj_moyenne_generale(sender, instance, **kwargs):
    instance.valeur_gn = (instance.valeur_cp * instance.bulletin.grille.poids_capacite + instance.valeur_sv * instance.bulletin.grille.poids_savoir_etre) / (instance.bulletin.grille.poids_capacite + instance.bulletin.grille.poids_savoir_etre)
pre_save.connect(maj_moyenne_generale, sender=Moyenne)

class Note(models.Model):
    bulletin = models.ForeignKey(Bulletin)
    capacite = models.ForeignKey(Capacite, null=True, blank=True)
    savoir = models.ForeignKey(SavoirEtre, null=True, blank=True)
    valeur = models.DecimalField(max_digits=3, decimal_places=1)
    # Indice dans la liste des annees (0, 1 etc) 
    annee = models.PositiveIntegerField(u'Année')
    date_modification = models.DateTimeField(auto_now=True)
    auteur_modification = models.ForeignKey(User)

    def sujet(self):
        """
        Méthode utilisée dans le vue liste admin
        """
        if self.capacite:
            return self.capacite.libelle
        return self.savoir.libelle
    
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
    ensemble de capacites
    
    Doit etre modifiable par l'eleve ce qui necessite un login/password pour les eleves
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
