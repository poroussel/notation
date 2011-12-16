# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from cfai.notation.models import *

class Command(BaseCommand):
    help = u'Réinitialisation des mots de passe des tuteurs et des chargés de promotion et envoi de nouveaux emails'

    def handle(self, *args, **options):
        users = User.objects.all()
        current_site = Site.objects.get_current()
        for u in users:
            profil = u.get_profile()
            if profil.is_tuteur() or profil.is_formateur():
                u.set_password(u.username)
                u.save()
                if len(u.email) > 0:
                    body = render_to_string('maj_compte.txt', {'profil' : profil, 'site' : current_site})
                    send_mail(u'[CFAI/ENSMM] Mise à jour de votre compte', body, settings.SERVER_EMAIL, [u.email], fail_silently=True)
