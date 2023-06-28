# -*- coding: utf-8 -*-

import os.path
import unicodedata

from datetime import date

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.signals import user_logged_in
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib import messages
from django.contrib.auth import logout
from django.utils.encoding import smart_unicode

class Suppression(models.Model):
    """
    On utilise quelque chose comme
    file:///usr/share/doc/python-django-doc/html/ref/contrib/contenttypes.html#generic-relations
    pour avoir un lien vers l'objet supprimé et donc acceder facilement
    a ses attributes et methodes
    """
    createur = models.ForeignKey(User, editable=False)
    date_creation = models.DateField(u'Date de la suppression', auto_now_add=True)
    raison = models.TextField('Motif de la suppression')
    content_type = models.ForeignKey(ContentType, editable=False)
    object_id = models.PositiveIntegerField(editable=False)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return u'Suppression de %s par %s le %s' % (self.content_object, self.createur.get_full_name(), self.date_creation)

def supprimer_objet(obj, user, reason):
    obj.suppression = Suppression.objects.create(createur = user, raison = reason, content_object = obj)
    obj.save()

TYPES = (('e', u'Apprenti'),
         ('t', u'Tuteur entreprise'),
         ('f', u'Tuteur académique'),
         ('a', u'Administratif'),
         ('p', u'Pilotage'),
         ('F', u'Tuteur académique et Pilotage'))

APPRECIATIONS = (('v', u'Non renseigné'),
                 ('a', u'Acquis'),
                 ('n', u'Non acquis'),
                 ('e', u'En cours d\'acquisition'),
                 ('p', u'Non applicable'))

NOTES = ((1, '1'),
         (2, '2'),
         (3, '3'),
         (4, '4'),
         (5, '5'))

NOMS_ANNEES = [u'1ère année', u'2ème année', u'3ème année']

class ProfilUtilisateur(models.Model):
    user = models.OneToOneField(User, unique=True)
    user_type = models.CharField(u'Type', max_length=1, default='a', choices=TYPES)
    password_modified = models.BooleanField(default=False, editable=True)
    phone_number = models.CharField(u'N° de téléphone', max_length=15, blank=True)
    suppression = models.OneToOneField(Suppression, null=True, blank=True, editable=False)

    def __unicode__(self):
        return u'%s - %s' % (self.user.get_full_name(), self.get_user_type_display())

    def is_tuteur(self):
        return self.user_type == 't'
    def is_eleve(self):
        return self.user_type == 'e'
    def is_formateur(self):
        return self.user_type == 'f' or self.user_type == 'F'

    def is_administratif(self):
        return self.user_type == 'a'
    def is_pilote(self):
        return self.user_type == 'p' or self.user_type == 'F'
    def is_manitou(self):
        return self.is_administratif() or self.is_pilote()

    def _nom_complet(self):
        return '%s %s' % (self.user.last_name, self.user.first_name)
    nom_complet = property(_nom_complet)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profil, created = ProfilUtilisateur.objects.get_or_create(user=instance)
post_save.connect(create_user_profile, sender=User, dispatch_uid='create_user_profile')

def check_user(sender, request, user, **kwargs):
    profile = user.get_profile()
    if not profile.password_modified:
        messages.warning(request, u'Vous devez modifier votre mot de passe !')

    if profile.is_eleve():
        bulletins = Bulletin.objects.filter(eleve=user)
        if all(b.grille.archive for b in bulletins):
            messages.error(request, u"Vous n'avez plus accès au site")
            user.is_active = False
            user.save()
            logout(request)

user_logged_in.connect(check_user, sender=User, dispatch_uid='user_logged_in')


class Ecole(models.Model):
    class Meta:
        verbose_name = u'Ecole'
        verbose_name_plural = u'Ecoles'

    nom = models.CharField(max_length=100, blank=False)
    calcul_note = models.BooleanField(u'Calcul automatique des notes', default=False)
    logo = models.CharField(u'Nom du fichier logo', max_length=100, blank=False)
    date_creation = models.DateTimeField(u'Date création', auto_now_add=True)

    def __unicode__(self):
        return u'%s' % (self.nom)

class Formation(models.Model):
    libelle = models.CharField(u'Libellé', max_length=80)
    # alter table notation_formation drop column duree;
    # duree = models.PositiveIntegerField(u'Durée en années de la formation')
    # Après création de l'ENSMM comme école d'id 1
    # alter table notation_formation add column ecole_id integer not null unique references "notation_ecole" ("id") default 1
    ecole = models.ForeignKey(Ecole, verbose_name='Ecole')

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
    # Les poids ne sont plus utilisés et pourront être supprimés après filtrage des données
    poids_capacite = models.PositiveIntegerField(u'Poids de la moyenne des capacités dans la moyenne générale', default=1, editable=False)
    poids_savoir_etre = models.PositiveIntegerField(u'Poids de la moyenne des savoirs être dans la moyenne générale', default=1, editable=False)
    # alter table notation_grillenotation add column archive bool not null default false
    archive = models.BooleanField(u'Grille archivée (plus de modification)', default=False)

    def __unicode__(self):
        return u'%s / %d - %d' % (self.frm.libelle, self.promotion, self.promotion + self.duree)

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


class Entreprise(models.Model):
    class Meta:
        ordering = ['nom']

    nom = models.CharField(u'Nom', max_length=80)
    description = models.TextField(u'Adresse', blank=True)
    telephone = models.CharField(u'N° de téléphone', max_length=15, blank=True)
    fax = models.CharField(u'N° de fax', max_length=15, blank=True)

    def __unicode__(self):
        return self.nom

    @models.permalink
    def get_absolute_url(self):
        return ('detail_entreprise', [self.id])


class BulletinApprentiNonSupprime(models.Manager):
    def get_query_set(self):
        return super(BulletinApprentiNonSupprime, self).get_query_set().filter(eleve__profilutilisateur__suppression=None)
class BulletinApprentiSupprime(models.Manager):
    def get_query_set(self):
        return super(BulletinApprentiSupprime, self).get_query_set().exclude(eleve__profilutilisateur__suppression=None)
class BulletinApprenti(models.Manager):
    def get_query_set(self):
        return super(BulletinApprenti, self).get_query_set()

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
    # FIXME : remplacé par le modèle CommentaireGeneral
    commentaires_generaux = models.TextField(u'Commentaires généraux')
    date_modification = models.DateTimeField(auto_now=True)
    auteur_modification = models.ForeignKey(User, related_name='auteur', null=True)

    # alter table notation_bulletin add column reunion_ma bool not null default false
    reunion_ma = models.BooleanField(u'Tuteur en réunion MA', default=False)

    objects = BulletinApprentiNonSupprime()
    supprimes = BulletinApprentiSupprime()
    tous = BulletinApprenti()

    def __unicode__(self):
        return u'Bulletin de %s (%s / %s)' % (self.eleve.get_profile().nom_complet, self.grille, self.entreprise)

    @models.permalink
    def get_absolute_url(self):
        return ('bulletin', [self.id])

    def archive(self):
        return self.grille.archive

    def calcul_moyenne_competence(self, annee, user):
        """
        Calcul la moyenne compétence de ce bulletin pour une année
        """
        annee = int(annee)
        themes = self.grille.theme_set.all()
        notes = Note.objects.filter(bulletin=self, theme__in=list(themes), annee=annee).values_list('valeur', flat=True)
        if len(notes) > 0:
            total = sum(float(n) for n in notes)
        else:
            total = 0.0
        if len(themes) > 0:
            moyenne = total / len(themes)
        else:
            moyenne = 0
        moy, created = Moyenne.objects.get_or_create(bulletin=self, annee=annee, defaults={'valeur_cp' : moyenne})
        if not created:
            moy.valeur_cp = moyenne
            moy.save()
        self.auteur_modification = user
        self.save()

    def calcul_moyenne_savoir(self, annee, user):
        """
        Calcul la moyenne savoir être de ce bulletin pour une année
        """
        annee = int(annee)
        savoirs = self.grille.savoiretre_set.all()
        notes = Note.objects.filter(bulletin=self, annee=annee, savoir__in=savoirs).values_list('valeur', flat=True)
        if len(notes) > 0:
            somme = sum(float(n) for n in notes)
        else:
            somme = 0.0
        somme += len(savoirs) - len(notes)
        if len(savoirs) > 0:
            moyenne = somme * 4 / len(savoirs)
        else:
            moyenne = 0
        moy, created = Moyenne.objects.get_or_create(bulletin=self, annee=annee, defaults={'valeur_sv' : moyenne})
        if not created:
            moy.valeur_sv = moyenne
            moy.save()
        self.auteur_modification = user
        self.save()

    def pourcentage_saisie(self, annee, id_theme):
        ens_theme = self.grille.ensemblecapacite_set.filter(theme=id_theme)
        # Ensemble des capacites pour ce theme
        ens_capa = Capacite.objects.filter(ensemble__in=list(ens_theme))
        # Ensemble des evaluations differentes de 'Non renseigne'
        ens_appr = self.evaluation_set.filter(annee=annee, capacite__in=list(ens_capa)).exclude(valeur='v')
        # Pourcentage
        if len(ens_capa) > 0:
            prc = len(ens_appr) * 100 / len(ens_capa)
        else:
            prc = 0
        return prc


def normalize_str(ustr):
    """
    Supprime les caractères spéciaux d'une chaine de caractères
    (unicode ou str en utf-8) et retourne une chaîne str utf-8
    """
    data = smart_unicode(ustr)
    return ''.join(c for c in unicodedata.normalize('NFD', data) if unicodedata.category(c) != 'Mn')

def upload_to(instance, filename):
    return '%.04d/%d/%s' % (instance.bulletin.grille.promotion, instance.bulletin.id, normalize_str(filename).replace(' ', '_'))

class PieceJointe(models.Model):
    class Meta:
        verbose_name = u'Pièce Jointe'
        verbose_name_plural = u'Pièces Jointes'

    fichier = models.FileField(upload_to=upload_to)
    bulletin = models.ForeignKey(Bulletin, editable=False)
    description = models.CharField(max_length=100, blank=False)
    date_creation = models.DateTimeField(u'Date création', auto_now_add=True)

    def nom_fichier(self):
        return os.path.basename(self.fichier.path)

    def __unicode__(self):
        return u'%s : %s' % (self.bulletin, self.nom_fichier())

class Theme(models.Model):
    """
    Un thème regroupe plusieurs ensemble de capacités.
    Une note sur 20 est attribuée pour chaque thème.

    Chaque thème est liée à une grille et comporte
    un libellé et une position dans la grille globale
    """
    class Meta:
        verbose_name = u'Thème'
        verbose_name_plural = u'Thèmes'
        ordering = ['grille', 'position']
        unique_together = ('grille', 'position')

    grille = models.ForeignKey(GrilleNotation)
    position = models.PositiveIntegerField()
    libelle = models.CharField(u'Libellé', max_length=200)

    def __unicode__(self):
        return self.libelle

class EnsembleCapacite(models.Model):
    class Meta:
        verbose_name = u'Ensemble de capacités'
        verbose_name_plural = u'Ensembles de capacités'
        ordering = ['grille', 'numero']
        unique_together = ('grille', 'numero')

    grille = models.ForeignKey(GrilleNotation)
    theme = models.ForeignKey(Theme)
    numero = models.PositiveIntegerField()
    libelle = models.CharField(u'Libellé', max_length=200)

    def precedent(self):
        precedents = EnsembleCapacite.objects.filter(grille=self.grille, numero=self.numero - 1)
        if precedents:
            return precedents[0]
        return None

    def suivant(self):
        suivants = EnsembleCapacite.objects.filter(grille=self.grille, numero=self.numero + 1)
        if suivants:
            return suivants[0]
        return None

    def __unicode__(self):
        return u'%d %s / %s' % (self.numero, self.libelle, self.grille)

class Capacite(models.Model):
    class Meta:
        verbose_name = u'Capacité'
        verbose_name_plural = u'Capacités'
        ordering = ['ensemble', 'numero']
        unique_together = ('ensemble', 'numero')

    ensemble = models.ForeignKey(EnsembleCapacite)
    numero = models.PositiveIntegerField()
    libelle = models.CharField(u'Libellé', max_length=200)
    # Ne sert plus, garder la définition pour retour arrière
    an_1 = models.BooleanField(NOMS_ANNEES[0], editable=False)
    an_2 = models.BooleanField(NOMS_ANNEES[1], editable=False)
    an_3 = models.BooleanField(NOMS_ANNEES[2], editable=False)
    code_annee = models.CharField(max_length=3, editable=False)

    def __unicode__(self):
        return u'%d.%d %s'% (self.ensemble.numero, self.numero, self.libelle)

class SavoirEtre(models.Model):
    class Meta:
        verbose_name = u'Savoir être'
        verbose_name_plural = u'Savoirs être'

    grille = models.ForeignKey(GrilleNotation)
    libelle = models.CharField(u'Libellé', max_length=200)
    # Ne sert plus, garder la définition pour retour arrière
    an_1 = models.BooleanField(NOMS_ANNEES[0], editable=False)
    an_2 = models.BooleanField(NOMS_ANNEES[1], editable=False)
    an_3 = models.BooleanField(NOMS_ANNEES[2], editable=False)
    code_annee = models.CharField(max_length=3, editable=False)

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
        return u'Moyenne de %s pour la %s' % (self.bulletin.eleve.get_profile().nom_complet, NOMS_ANNEES[self.annee])

def maj_moyenne_generale(sender, instance, **kwargs):
    instance.valeur_gn = (float(instance.valeur_cp) + float(instance.valeur_sv) ) / 2
pre_save.connect(maj_moyenne_generale, sender=Moyenne)

class Evaluation(models.Model):
    """
    Les capacités ne sont plus notées individuellement mais évaluées.
    """
    bulletin = models.ForeignKey(Bulletin)
    capacite = models.ForeignKey(Capacite)
    valeur = models.CharField(max_length=1, default='v', choices=APPRECIATIONS)
    annee = models.PositiveIntegerField(u'Année')
    date_modification = models.DateTimeField(auto_now=True)
    auteur_modification = models.ForeignKey(User)

    def __unicode__(self):
        return u'Évaluation de %s pour la capacité %s'% (self.bulletin.eleve.get_profile().nom_complet, self.capacite)

class Note(models.Model):
    """
    Une note peut être affectée à un savoir être
    ou à un thème
    """
    bulletin = models.ForeignKey(Bulletin)
    theme = models.ForeignKey(Theme, null=True, blank=True)
    savoir = models.ForeignKey(SavoirEtre, null=True, blank=True)
    valeur = models.DecimalField(max_digits=3, decimal_places=1)
    annee = models.PositiveIntegerField(u'Année')
    date_modification = models.DateTimeField(auto_now=True)
    auteur_modification = models.ForeignKey(User)

    def sujet(self):
        """
        Méthode utilisée dans le vue liste admin
        """
        if self.theme:
            return self.theme.libelle
        return self.savoir.libelle

    def eleve(self):
        """
        Méthode utilisée dans le vue liste admin
        """
        return self.bulletin.eleve.get_profile().nom_complet

    def __unicode__(self):
        if self.theme:
            return u'Note de %s pour la capacité %s'% (self.bulletin.eleve.get_profile().nom_complet, self.theme)
        return u'Note de %s pour le savoir être %s'% (self.bulletin.eleve.get_profile().nom_complet, self.savoir)

class Commentaire(models.Model):
    """
    Permet le stockage d'un commentaire libre pour un bulletin, un
    ensemble de capacites et une annee

    Doit etre modifiable par l'eleve ce qui necessite un login/password pour les eleves
    """
    class Meta:
        verbose_name = u'Commentaire'
        verbose_name_plural = u'Commentaires'

    bulletin = models.ForeignKey(Bulletin)
    ensemble = models.ForeignKey(EnsembleCapacite)
    texte = models.TextField()
    annee = models.PositiveIntegerField(u'Année', default=0)
    date_modification = models.DateTimeField(auto_now=True)
    auteur_modification = models.ForeignKey(User)

    def eleve(self):
        """
        Méthode utilisée dans le vue liste admin
        """
        return self.bulletin.eleve.get_profile().nom_complet

    def __unicode__(self):
        return u'Commentaire de %s pour le groupe %s' % (self.bulletin.eleve.get_full_name(), self.ensemble)

class CommentaireGeneral(models.Model):
    """
    Permet le stockage d'un commentaire general (savoir etreà par un bulletin et
    par année
    """
    class Meta:
        verbose_name = u'Commentaire général'
        verbose_name_plural = u'Commentaires généraux'

    bulletin = models.ForeignKey(Bulletin)
    texte = models.TextField()
    annee = models.PositiveIntegerField(u'Année', default=0)
    date_modification = models.DateTimeField(auto_now=True)
    auteur_modification = models.ForeignKey(User)

    def eleve(self):
        """
        Méthode utilisée dans le vue liste admin
        """
        return self.bulletin.eleve.get_profile().nom_complet

    def __unicode__(self):
        return u'Commentaire général de %s pour l\'année %d' % (self.bulletin.eleve.get_full_name(), self.annee)
