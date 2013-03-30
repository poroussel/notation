# -*- coding: utf-8 -*-

import time
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from cfai.notation.models import *

class Command(BaseCommand):
    help = u'Réinitialisation des mots de passe des tuteurs et envoi de nouveaux emails'

    def handle(self, *args, **options):
        users = User.objects.all()
        current_site = Site.objects.get_current()
        for u in users:
            profil = u.get_profile()
            if profil.is_tuteur():
                password = User.objects.make_random_password()
                u.set_password(password)
                u.save()
                profil.password_modified = False
                profil.save()
                if len(u.email) > 0:
                    body = render_to_string('maj_compte.txt', {'profil' : profil, 'site' : current_site, 'password' : password})
                    print u'Email envoyé à %s <%s> avec mot de passe : %s' % (profil.nom_complet, u.email, password)
                    send_mail(u'[CFAI/ENSMM] Mise à jour de votre compte', body, settings.SERVER_EMAIL, [u.email], fail_silently=True)
                    time.sleep(5)

