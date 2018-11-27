import os, sys

sys.path.append('/home/notation')
sys.path.append('/home/notation/cfai')
os.environ['DJANGO_SETTINGS_MODULE'] = 'cfai.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
