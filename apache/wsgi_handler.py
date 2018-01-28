import os, sys

sys.path.append('/opt/django-1.4.5')
sys.path.append('/home/www')
sys.path.append('/home/www/cfai')
os.environ['DJANGO_SETTINGS_MODULE'] = 'cfai.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
