# Modification de juillet 2023

## Vue d'ensemble

* Ajout de la table Ecole qui permet définir pour chaque école
  son nom, son logo (à placer dans le répertoire static/images/)
  et si les notes calculées automatiquement

* Création de 2 écoles : ESMM et UTBM

* Chaque formation est reliée à une école, les formations existantes
  étant reliées à ENSMM

* Lorsque le calcul des notes est activé les champs de saisie sont
  visibles mais en lecture seule.

* Pour chaque page pour laquelle on peut déterminer un école, le
  logo de cette école est affiché. Lorsque le choix n'est pas possbile
  le logo de l'ITII est utilisé.

* Afin de simplifier l'ajout de nouvelles grilles de notation les
  commandes exportgrille et importgrille ont été ajoutées.

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
