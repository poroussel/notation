#!/bin/bash

python manage.py dumpdata --indent=2 notation.grillenotation notation.theme notation.ensemblecapacite notation.capacite notation.savoiretre > notation/fixtures/ngrilles.json
