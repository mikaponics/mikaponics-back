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
from foundation.models import Instrument, InstrumentAnalysis, Device, TimeSeriesDatum


class Command(BaseCommand):
    help = _('Command will generate an analysis of the instrument for a particular date and time range.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py compute_instrument_analysis 12 "2019-03-03 4:00 AM" "2019-03-03 5:00 AM" "America/Toronto"
        """
        # The instrument ID to based this analysis on.
        parser.add_argument('instrument_id', nargs='+', type=int)

        # The start date and time this analysis will be based on.
        parser.add_argument('start_dt', nargs='+', type=str)

        # The end date and time this analysis will be based on.
        parser.add_argument('finish_dt', nargs='+', type=str)

        # The timezone name that the start/finish date and times are based on.
        parser.add_argument('timezone_name', nargs='+', type=str)

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(_('%(dt)s | CIA | Started running.') % {
                'dt': str(timezone.now())
            })
        )

        # Extract our console arguments.
        instrument_id = options['instrument_id'][0]
        start_dt = options['start_dt'][0]
        finish_dt = options['finish_dt'][0]
        timezone_name = options['timezone_name'][0]

        # Lookup our instrument.
        try:
            instrument = Instrument.objects.get(id=instrument_id)
        except Exception as e:
            raise CommandError(_('Instrument was not found.'))

        # Convert to our datatime.
        naive_start_dt = parse(start_dt)
        naive_finish_dt = parse(finish_dt)
        naive_start_dt = naive_start_dt.replace(second=0,microsecond=0)
        naive_finish_dt = naive_finish_dt.replace(second=0,microsecond=0)
        local_timezone = pytz.timezone(timezone_name)
        aware_start_dt = naive_start_dt.replace(tzinfo=local_timezone)
        aware_finish_dt = naive_finish_dt.replace(tzinfo=local_timezone)

        # For debugging purposes only.
        self.stdout.write(
            self.style.SUCCESS(_('%(dt)s | CIA | Processing from %(start_dt)s to %(finish_dt)s.') % {
                'dt': str(timezone.now()),
                'start_dt': str(aware_start_dt),
                'finish_dt': str(aware_finish_dt),
            })
        )

        # Run our code.
        data = TimeSeriesDatum.objects.filter(
            instrument=instrument,
            timestamp__range=[aware_start_dt, aware_finish_dt]
        ).order_by('value') # Order by value b/c we need to find the median.
        self.begin_processing(instrument, aware_start_dt, aware_finish_dt, data)

    def begin_processing(self, instrument, aware_start_dt, aware_finish_dt, data):
        # Variables used in our computations.
        max_value = 0
        max_timestamp = None
        min_value = 999999
        min_timestamp = None
        values_array = data.values_list('value', flat=True)

        # Iterate through all the data and generate our statistics.
        for datum in data.iterator(chunk_size=250):
            '''
            Find the largest value
            '''
            if datum.value > max_value:
                max_value = datum.value
                max_timestamp = datum.timestamp

            '''
            Find the smallest value
            '''
            if datum.value < min_value:
                min_value = datum.value
                min_timestamp = datum.timestamp


            #TODO:
            # mode_value
            # range_value
            #

        '''
        Find the mean.
        '''
        mean_value = mean(values_array)

        '''
        Find the median.
        '''
        median_value = median(values_array)

        '''
        Find the mode.
        '''
        try:
            mode_value = mode(values_array)
            mode_values_array = None
        except StatisticsError as e:
            mode_value = None
            mode_values_array = []

            from collections import Counter
            c_data = Counter(values_array)
            c_data.most_common()   # Returns all unique items and their counts
            most_common_tuple_list = c_data.most_common(1)  # Returns the highest occurring item
            most_common_tuple = most_common_tuple_list[0]
            most_common_list = list(most_common_tuple)
            mode_values_array = most_common_list

        '''
        Find the range.
        '''
        range_value = max_value - min_value

        '''
        Find the standard dev.
        '''
        stedv_value = stdev(values_array)

        '''
        Find the variance.
        '''
        variance_value = variance(values_array)

        '''
        Create our analysis.
        '''
        print("MAX", max_value,"at",max_timestamp)
        print("MIN", min_value,"at",min_timestamp)
        print("MEAN", mean_value)
        print("MEDIAN", median_value)
        print("MODE VALUE", mode_value)
        print("MODE VALUES", mode_values_array)
        print("RANGE", range_value)
        print("STEDV", stedv_value)
        print("VAR", variance_value)
        analysis, was_created = InstrumentAnalysis.objects.update_or_create(
            instrument=instrument,
            start_dt=aware_start_dt,
            finish_dt=aware_finish_dt,
            defaults={
                'instrument': instrument,
                'start_dt': aware_start_dt,
                'finish_dt': aware_finish_dt,
                'min_value': min_value,
                'min_timestamp': min_timestamp,
                'max_value': max_value,
                'max_timestamp': max_timestamp,
                'mean_value': mean_value,
                'median_value': median_value,
                'mode_value': mode_value,
                'mode_values': mode_values_array,
                'range_value': range_value,
                'stedv_value': stedv_value,
                'variance_value': variance_value,
            }
        )

        # For debugging purposes only.
        self.stdout.write(
            self.style.SUCCESS(_('%(dt)s | CIA | %(status)s analysis # %(id)s.') % {
                'dt': str(timezone.now()),
                'id': str(analysis.id),
                'status': 'Created' if was_created else 'Updated'
            })
        )
