# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User


class Entreprise:
    pass

class Eleve:
    """
    Un élève est encadré par un tuteur, supervisé par un formateur et
    lié à une grille de notation et une entreprise
    """
    pass

class Note:
    """
    Relie une note à un élève, une compétence et une année (1, 2 ou 3)
    """
    pass

class CommentaireCompetence:
    """
    Permet le stockage d'un commentaire libre pour un élève et un
    ensemble de compétences
    
    Doit être modifiable par l'élève ce qui nécessite un login/password pour les élèves
    """
    pass

class Competence:
    """
    """
    pass

class EnsembleCompetence:
    """
    """
    pass

class GrilleNotation:
    """
    """
    pass
