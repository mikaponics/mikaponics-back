# -*- coding: utf-8 -*-
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

from djmoney.money import Money
from oauthlib.common import generate_token

from foundation.constants import *
from foundation.models import Production


class Command(BaseCommand):
    """
    EXAMPLE:
    python manage.py evaluate_production_by_id 1
    """

    help = _('Command evaluates the production by the inputted ID.')

    def add_arguments(self, parser):
        parser.add_argument('id', nargs='+', type=int)

    def handle(self, *args, **options):
        utc_today = timezone.now()

        # For debugging purposes only.
        self.stdout.write(
            self.style.SUCCESS(_('%(dt)s | EVALUATION | Started running.') % {
                'dt': str(timezone.now())
            })
        )

        try:
            for id in options['id']:
                alert = Production.objects.get(id=id)
                self.begin_processing(alert)

        except Production.DoesNotExist:
            # For debugging purposes only.
            raise CommandError(_('%(dt)s | EVALUATION | Production does not exist with the id.') % {
                'dt': str(timezone.now())
            })

        # For debugging purposes only.
        self.stdout.write(
            self.style.SUCCESS(_('%(dt)s | EVALUATION | Finished running.') % {
                'dt': str(timezone.now())
            })
        )

    def begin_processing(self, production):
        for production_crop in production.crops.all():
            self.begin_processing_production_crop(production_crop)

    def begin_processing_production_crop(self, production_crop):
        print("TODO:", production_crop)
