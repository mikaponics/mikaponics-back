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
from foundation.models import Production, ProductionCrop, CropDataSheet, TimeSeriesDatum


class Command(BaseCommand):
    """
    DESCRIPTION:
    Command will process a `Production` and provide an evaluation score.

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

                # Always reset our crop evaluation before beginning...
                production_crop.evaluation_score = None
                production_crop.evaluation_error = None
                production_crop.evaluation_dict = {}
                production_crop.save()

                # Begin our evaluation!
                self.begin_processing_production_crop(production_crop)

        with freeze_time(production.last_modified_at):
            self.begin_processing_production(production)

    def begin_processing_production(self, production):
        # Refresh the latest data and then clear it before beginning our
        # evaluation of the `Production` object.
        production.refresh_from_db()
        production.evaluation_has_error = False
        production.evaluation_score = None
        production.evaluated_at = None

        # Evaluate the `Production` object.
        total_score = 0
        has_error = False
        for production_crop in production.crops.all():
            if production_crop.evaluation_score:
                total_score += production_crop.evaluation_score
            if production_crop.evaluation_error:
                has_error = True

        if has_error:
            production.evaluation_has_error = True
        production.evaluation_score = total_score
        production.evaluated_at = timezone.now()
        production.save()
        self.stdout.write(
            self.style.SUCCESS(_('%(dt)s | EVALUATION | Production %(slug)s finished.') % {
                'dt': str(timezone.now()),
                'slug': production.slug
            })
        )
        return # Stop this ETL.

    def begin_processing_production_crop(self, production_crop):
        # STEP 1:
        # CHECK TO SEE IF WE GET AN "INDETERMINATE" ERROR WHICH IS CAUSED IF
        # THE USER SELECTED THE "OTHER" CROP OPTION. WE NEED TO STOP THIS
        # FUNCTION IF THIS ERROR OCCURES EARLY ON.
        production_crop = self.process_is_crop_indeterminate(production_crop)
        if production_crop.evaluation_error is not None:
            self.stdout.write(
                self.style.WARNING(_('%(dt)s | EVALUATION | Production crop %(slug)s finished evaluation with error(s).') % {
                    'dt': str(timezone.now()),
                    'slug': production_crop.slug
                })
            )
            return # Stop this ETL.

        # STEP 2:
        # RUN THE EVALUATION FOR THE PARTICULAR PRODUCTION CROP.
        production_crop = self.process_crop_score(production_crop) #TODO: BREAK UP!

        self.stdout.write(
            self.style.SUCCESS(_('%(dt)s | EVALUATION | Production crop %(slug)s finished evaluation.') % {
                'dt': str(timezone.now()),
                'slug': production_crop.slug
            })
        )

    def process_is_crop_indeterminate(self, production_crop):
        """
        Function will check to see if the `ProductionCrop` is `Other` so we
        can generate an error, else continue with our evaluation.
        """
        # The user selected the "Other" option in the data sheet.
        if production_crop.data_sheet.type_of == CropDataSheet.TYPE_OF.NONE:
            production_crop.evaluation_error = "Indeterminate - You are growing a `other` crop which we do not support"
            production_crop.save()
            self.stdout.write(
                self.style.SUCCESS(_('%(dt)s | EVALUATION | Production crop %(slug)s has become evaluation score is indterminate.') % {
                    'dt': str(timezone.now()),
                    'slug': production_crop.slug
                })
            )
        return production_crop

    def process_crop_score(self, production_crop):
        """
        Function will calculate the `evaluation_score` for the production crop.
        """
        # ALGORITHM
        # (1) Fetch all the conditions for evaluation for this crop at this
        #     crops current life-cycle stage.
        # (2) Fetch the device running for this production.
        # (3) Count how many conditions there are. (Ex: 5)
        # (4) Fetch the latest time-series datum for the device.

        stage = production_crop.stage
        conditions = production_crop.data_sheet.conditions.filter(stage=stage).order_by('id')
        device = production_crop.production.device
        conditions_count = conditions.count()
        pass_count = 0

        for condition in conditions.all():
            did_pass, has_error = self.evaluate(production_crop, device, condition)
            if did_pass:
                pass_count += 1
            if has_error:
                self.stdout.write(
                    self.style.ERROR(_('%(dt)s | EVALUATION | Stopped evaluating %(instrument)s.') % {
                        'dt': str(timezone.now()),
                        'instrument': condition.get_pretty_instrument_type_of()
                    })
                )
                break; # STOP THIS FOR-LOOP.

        # ATTACH TIMESTAMP OF WHEN THE EVALUATION OCCURED FOR THE PRODUCTION CROP.
        production_crop.evaluated_at = timezone.now()

        # COMPUTER OUR SCORE.
        try:
            production_crop.evaluation_score = (pass_count / conditions_count) * 100
        except ZeroDivisionError:
            production_crop.evaluation_score = None

        # SAVE OUR OBJECT.
        production_crop.save()

        # RETURN OUR EVALUATED PRODUCTION CROP.
        return production_crop

    def evaluate(self, production_crop, device, condition):
        self.stdout.write(
            self.style.SUCCESS(_('%(dt)s | EVALUATION | Evaluating %(instrument)s condition.') % {
                'dt': str(timezone.now()),
                'instrument': condition.get_pretty_instrument_type_of()
            })
        )

        # STEP 1:
        # CHECK TO SEE IF WE HAVE THE SUPPORTED INSTRUMENT. IF NOT THEN WE FAIL.
        instrument = device.instruments.filter(type_of=condition.get_transcoded_instrument_type_of()).first()
        if instrument is None:
            self.stdout.write(
                self.style.WARNING(_('%(dt)s | EVALUATION | Failed evaluating condition because %(instrument)s D.N.E..') % {
                    'dt': str(timezone.now()),
                    'instrument': condition.get_pretty_instrument_type_of()
                })
            )
            production_crop.evaluation_error = "Failed evaluating because "+condition.get_pretty_instrument_type_of()+" D.N.E.."
            production_crop.save()
            return False, True

        # STEP 2:
        # LOOKUP THE LATEST TIME-SERIES-DATA FOR THIS INSTRUMENT AND FAIL THE
        # EVALUATION IF (1) THE VALUE IS NULL OR (2) THE TIMESTAMP IS TOO OLD
        # OR (3) NO DATA HAS BEEN RETURNED.
        try:
            datum = instrument.time_series_data.latest('timestamp')
            if datum.value is None: # (1)
                self.stdout.write(
                    self.style.WARNING(_('%(dt)s | EVALUATION | Failed evaluating condition because %(instrument)s because latest data is null.') % {
                        'dt': str(timezone.now()),
                        'instrument': condition.get_pretty_instrument_type_of()
                    })
                )
                production_crop.evaluation_error = "Failed evaluating because instrument\'s latest data is null."
                production_crop.save()
                return False, True

            # (2) TODO - timstamp too old.
        except TimeSeriesDatum.DoesNotExist: # (3)
            self.stdout.write(
                self.style.WARNING(_('%(dt)s | EVALUATION | Failed evaluating condition because %(instrument)s has no data.') % {
                    'dt': str(timezone.now()),
                    'instrument': condition.get_pretty_instrument_type_of()
                })
            )
            production_crop.evaluation_error = "Failed evaluating because instrument has no data."
            production_crop.save()
            return False, True

        # STEP 3:
        # EVALUATE THE CONDITION WITH OUR LATEST DATA AND LOG WHERE OUR
        # CONDITION FAILS SO WE WILL KNOW WHAT HAPPENED TO OUR SCORE.
        is_over = datum.value > condition.max_value
        if is_over:
            production_crop.evaluation_dict[condition.get_pretty_instrument_type_of()] = {
                'failure_reason': 'is_over',
                'condition_id': condition.id,
                'condition_type_of': condition.get_pretty_instrument_type_of(),
                'actual_value': datum.value,
                'max_value': condition.max_value,
            }
            production_crop.save()

        is_under = datum.value < condition.min_value
        if is_under:
            production_crop.evaluation_dict[condition.get_pretty_instrument_type_of()] = {
                'failure_reason': 'is_under',
                'condition_id': condition.id,
                'condition_type_of': condition.get_pretty_instrument_type_of(),
                'actual_value': datum.value,
                'min_value': condition.min_value,
            }
            production_crop.save()

        # Return our final evaluation and no error status.
        return (is_over == False and is_under == False), False
