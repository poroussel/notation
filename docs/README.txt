Développé avec :

 - python 2.7.3
 - django 1.4.22
 - xlwt 1.3.0


Mise à jour de la base de données :

python manage.py dumpdata --indent=2 sites auth notation > notation/fixtures/dump.json
rm cfai.db
python manage.py syncdb
python manage.py loaddata dump
