# Django settings for cfai project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG
SERVE_STATIC = True

ADMINS = (
    ('Philippe Roussel', 'philippe.roussel@octets.fr'),
)

MANAGERS = ADMINS

EMAIL_HOST = 'localhost'
EMAIL_PORT = '25'
EMAIL_SUBJECT_PREFIX = '[Notation]'
SERVER_EMAIL = 'webmaster@formation-industries-fc.fr'
DEFAULT_FROM_EMAIL = SERVER_EMAIL

DATABASES_PROD = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '/home/notation/cfai/cfai.db',  # Or path to database file if using sqlite3.
        'USER': '',                             # Not used with sqlite3.
        'PASSWORD': '',                         # Not used with sqlite3.
        'HOST': '',                             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                             # Set to empty string for default. Not used with sqlite3.
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'cfai.db',                      # Or path to database file if using sqlite3.
        'USER': '',                             # Not used with sqlite3.
        'PASSWORD': '',                         # Not used with sqlite3.
        'HOST': '',                             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                             # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fr-FR'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"
import os.path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

FILE_UPLOAD_PERMISSIONS = 0644
FILE_UPLOAD_HANDLERS = ('django.core.files.uploadhandler.TemporaryFileUploadHandler',)

STATIC_ROOT= os.path.join(PROJECT_ROOT, 'static')
STATIC_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 't9bm+or2g6(_(u^2r9gfo!yox!zo_^v%)%%u3o&gc*(2-k4s75'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.Loader',
)

AUTH_PROFILE_MODULE = 'notation.ProfilUtilisateur'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'notation.views.SearchMiddleware',
)

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

ROOT_URLCONF = 'cfai.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'cfai.notation',
)

# Definition de la valeur des appreciations pour chaque annee d'une formation
# La premiere ligne correspond a la premiere annee de formation et ainsi de suite.
# La cle correspond a l'une des appreciations :
#   * v : Non evalue
#   * n : Notion
#   * e : Application tutoree
#   * a : Application autonome
#   * m : Maitrise
#   * p : Non applicable
#
# Une modification de ces valeurs necessite un redemarrage du serveur pour
# etre prise en compte.
VALEUR_APPRECIATION = [
    {'p': None, 'v': None, 'n': 12, 'e': 13, 'a': 15, 'm': 18},
    {'p': None, 'v': None, 'n': 10, 'e': 13, 'a': 15, 'm': 18},
    {'p': None, 'v': None, 'n': 10, 'e': 13, 'a': 15, 'm': 18}
]
