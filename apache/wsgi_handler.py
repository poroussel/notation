import os, sys

sys.path.append('/home/www/cfai')
sys.path.append('/home/www/cfai/notation')
os.environ['DJANGO_SETTINGS_MODULE'] = 'notation.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
