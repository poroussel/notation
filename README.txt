Développé avec :

 - python 2.7.1
 - django 1.2.5
 - xlwt 0.7.2


Mise à jour de la base de données :

python manage.py dumpdata --indent=2 auth sites notation > notation/fixtures/dump.json
rm cfai.db
python manage.py syncdb
python manage.py loaddata dump
