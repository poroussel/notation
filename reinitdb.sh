#!/bin/bash

rm cfai.db
python manage.py syncdb
python manage.py loaddata dump-sansnotes
