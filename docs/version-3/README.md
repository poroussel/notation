# Modification de juillet 2023

## Vue d'ensemble

* Ajout de la table Ecole qui permet définir pour chaque école
  son nom, son logo (à placer dans le répertoire static/images/),
  si les notes calculées automatiquement et les poids des
  compétences et des savoirs être dans le calcul de la moyenne

* Création de 2 écoles : ESMM et UTBM

* Chaque formation est reliée à une école, les formations existantes
  étant reliées à ENSMM.

* Les moyennes générales sont calculées à l'aide des poids définis
  pour chaque école.

* Lorsque le calcul des notes est activé les champs de saisie sont
  visibles mais en lecture seule. Le bouton 'Enregistrer les notes
  compétences' n'apparaît pas.

* Pour chaque page pour laquelle on peut déterminer un école, le
  logo de cette école est affiché. Lorsque le choix n'est pas possbile
  le logo de l'ITII est utilisé.

* Mise à jour des appréciations possibles (Non évalué,
  Application autonome, Notion, Application tutorée,
  Maîtrise)

* Afin de simplifier l'ajout de nouvelles grilles de notation les
  commandes exportgrille et importgrille ont été ajoutées.

* La recherche intègre les profils utilisateurs

## Gestion des grilles

La commande `exportgrille` permet de générer un fichier json décrivant
le contenu d'une grille de notation. La commande attend en paramètre l'id
de la grille à exporter.

Par exemple pour la grille Mécanique 2022-2025 l'export est réalisé ainsi :

```
user@hostname:~/sources/cfai$ python manage.py exportgrille 32
Génération du ficher grille-32-2023-07-09.json
user@hostname:~/sources/cfai$
```

Pour créer une grille Mécanique 2024-2027 il suffit d'éditer le fichier
`grille-32-2023-07-09.json` et de modifier la valeur associée à la
clé `promotion` de 2022 à 2024. On importe ensuite la nouvelle grille
avec la commande :

```
user@hostname:~/sources/cfai$ python manage.py importgrille grille-32-2023-07-09.json
user@hostname:~/sources/cfai$
```

De la même façon la commande `importgrille` peut être utilisée pour créer
des grilles complètement nouvelles. Il suffit pour cela que la formation
ait été créée dans l'interface d'administration.
