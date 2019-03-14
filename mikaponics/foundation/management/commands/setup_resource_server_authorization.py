# -*- coding: utf-8 -*-
"""
Example:
python manage.py setup_resource_server_authorization "bart@mikasoftware.com"
"""
import logging
import os
import sys
from decimal import *
from django.db.models import Sum
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from oauthlib.common import generate_token
from oauth2_provider.models import (
    Application,
    AbstractApplication,
    AbstractAccessToken,
    AccessToken,
    RefreshToken
)

from foundation.models import User


class Command(BaseCommand):
    help = _('Adds a oAuth 2.0 application to the server.')

    # def add_arguments(self, parser):
    #     parser.add_argument('email', nargs='+', type=str)

    def handle(self, *args, **options):
        # email = options['email'][0]

        # user = User.objects.filter(email=email).first()
        # if user is None:
        #     raise CommandError(_('No user exists for entered email.'))

        application, created = Application.objects.update_or_create(
            name=settings.MIKAPONICS_RESOURCE_SERVER_NAME,
            defaults={
                "user": None,
                "name": settings.MIKAPONICS_RESOURCE_SERVER_NAME,
                "skip_authorization": True,
                "authorization_grant_type": AbstractApplication.GRANT_PASSWORD,
                "client_type": AbstractApplication.CLIENT_CONFIDENTIAL
            }
        )

        # Create our our access token.
        aware_dt = timezone.now()
        expires_dt = aware_dt.replace(aware_dt.year + 1776)
        access_token, created = AccessToken.objects.update_or_create(
            application=application,
            defaults={
                'user': None,
                'application': application,
                'expires': expires_dt,
                'token': generate_token(),
                'scope': 'read,write,introspection'
            },
            scope='read,write,introspection'
        )

        # STEP 3: Return our ID values.
        self.stdout.write(
            self.style.SUCCESS(_('Resource Server - Auth Type: %(type)s') % {
                'type': str(AbstractApplication.GRANT_PASSWORD)
            })
        )
        self.stdout.write(
            self.style.SUCCESS(_('Resource Server - Client ID: %(client_id)s') % {
                'client_id': application.client_id
            })
        )
        self.stdout.write(
            self.style.SUCCESS(_('Resource Server - Client Secret: %(client_secret)s') % {
                'client_secret': application.client_secret
            })
        )
        self.stdout.write(
            self.style.SUCCESS(_('Resource Server - Access Token: %(access_token)s') % {
                'access_token': str(access_token)
            })
        )
