# -*- coding: utf-8 -*-
import pytz
from statistics import mean, median, mode, stdev, variance, StatisticsError  # https://docs.python.org/3/library/statistics.html
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q, Prefetch
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from dateutil.parser import *

from foundation import constants
from foundation.models import InstrumentSimulator, TimeSeriesDatum


class Command(BaseCommand):
    help = _('Command will generate random time-series data for the instrument simulator.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py instrument_simulator_tick 1
        """
        # The instrument ID to based this analysis on.
        parser.add_argument('instrument_id', nargs='+', type=int)

    @transaction.atomic
    def handle(self, *args, **options):
        # Extract our console arguments.
        instrument_id = options['instrument_id'][0]

        # For debugging purposes only.
        self.stdout.write(
            self.style.SUCCESS(_('%(dt)s | IST | Started running for instrument simulator #%(id)s.') % {
                'dt': str(timezone.now()),
                'id': instrument_id
            })
        )

        # Lookup our simulator.
        try:
            simulator = InstrumentSimulator.objects.select_for_update().get(id=instrument_id)
            self.process_simulator(simulator)
        except InstrumentSimulator.DoesNotExist:
            raise CommandError(_('Instrument was not found.'))

    def process_simulator(self, simulator):
        pass
