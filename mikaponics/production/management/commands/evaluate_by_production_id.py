# -*- coding: utf-8 -*-
import logging
import os
import sys
from freezegun import freeze_time
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
from foundation.models import Production, ProductionCrop, CropDataSheet


class Command(BaseCommand):
    """
    EXAMPLE:
    python manage.py evaluate_by_production_id 1
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
                production = Production.objects.get(id=id)
                self.begin_processing(production)

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
        # Iterate through all the production crops and lock the last modified
        # time as is so we don't affect it based on the evaluation.
        for production_crop in production.crops.all():
            with freeze_time(production_crop.last_modified_at):
                self.begin_processing_production_crop(production_crop)

    def begin_processing_production_crop(self, production_crop):
        production_crop = self.process_is_indterminate(production_crop)

    def process_is_indterminate(self, production_crop):
        # CASE 1 OF 2:
        # The user selected the "Other" option in the data sheet.
        if production_crop.data_sheet.type_of == CropDataSheet.TYPE_OF.NONE:
            production_crop.is_evaluation_score_indeterminate = True
            production_crop.save()
            self.stdout.write(
                self.style.SUCCESS(_('%(dt)s | EVALUATION | Production crop %(slug)s has become evaluation score is indterminate.') % {
                    'dt': str(timezone.now()),
                    'slug': production_crop.slug
                })
            )
        # CASE 2 OF 2:
        # The user selected a non "Other" option in the data sheet.
        else:
            production_crop.is_evaluation_score_indeterminate = False
            production_crop.save()
        return production_crop
