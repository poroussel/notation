#!/bin/bash

python manage.py dumpdata --indent=2 notation.theme notation.ensemblecapacite notation.capacite > notation/fixtures/ngrilles.json
