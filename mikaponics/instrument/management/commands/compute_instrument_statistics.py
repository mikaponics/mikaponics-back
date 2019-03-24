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
    help = _('Command will generate and save the statistics for an instrument in a particular date and time range.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py compute_instrument_statistics 1
        """
        # The instrument ID to based this analysis on.
        parser.add_argument('instrument_id', nargs='+', type=int)

    @transaction.atomic
    def handle(self, *args, **options):
        # Extract our console arguments.
        instrument_id = options['instrument_id'][0]

        # For debugging purposes only.
        self.stdout.write(
            self.style.SUCCESS(_('%(dt)s | CIS | Started running for instrument #%(id)s.') % {
                'dt': str(timezone.now()),
                'id': instrument_id
            })
        )

        # Create datetime range we will be using.
        utc_now = timezone.now()
        utc_now = utc_now.replace(second=0, microsecond=0)
        utc_now_minus_24h = utc_now - timedelta(hours=24)
        utc_now_minus_48h = utc_now - timedelta(hours=48)
        utc_now_minus_72h = utc_now - timedelta(hours=72)

        # Lookup our instrument.
        try:
            instrument = Instrument.objects.get(id=instrument_id)
        except Exception as e:
            raise CommandError(_('Instrument was not found.'))

        # Find the most recent time series datum for this instrument.
        try:
            latest_datum = TimeSeriesDatum.objects.filter(
                Q(instrument=instrument)&
                ~Q(value=None)
            ).latest('timestamp')
        except TimeSeriesDatum.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(_('%(dt)s | CIS | Aborted execution for instrument #%(id)s because it has no data.') % {
                    'dt': str(timezone.now()),
                    'id': instrument_id
                })
            )
            return

        latest_measured_value = latest_datum.value if latest_datum else None
        latest_measured_at_utc = latest_datum.timestamp if latest_datum else None

        # Generate our statistics for the specific date-time ranges.
        last_24h_statistics = self.compute_statistics(instrument, utc_now_minus_24h, utc_now)
        # last_48h_statistics = self.compute_statistics(instrument, utc_now_minus_48h, utc_now)
        # last_72h_statistics = self.compute_statistics(instrument, utc_now_minus_72h, utc_now)

        # # For debugging purposes only.
        # print(last_24h_statistics)
        # print(last_48h_statistics)
        # print(last_72h_statistics)

        # Combine all our statistics into a single variable.
        statistics = {
            # ----------------------------| v1.0 |------------------------------
            # General information.
            'generated_at_utc': str(timezone.now()),
            'unit_of_measure': instrument.get_unit_of_measure(),
            'slug': instrument.slug,
            'absolute_url': instrument.get_absolute_url(),

            # Latest values
            'last_measured_value': latest_measured_value,
            'last_measured_at_utc': str(latest_measured_at_utc),

            # Last 24h statistics.
            'last_24h_min_value': last_24h_statistics.get('min_value', None),
            'last_24h_min_timestamp_at_utc': last_24h_statistics.get('min_timestamp_utc', None),
            'last_24h_max_value': last_24h_statistics.get('max_value', None),
            'last_24h_max_timestamp_at_utc': last_24h_statistics.get('max_timestamp_utc', None),
            'last_24h_mean_value': last_24h_statistics.get('mean_value', None),
            'last_24h_median_value': last_24h_statistics.get('median_value', None),
            'last_24h_mode_value': last_24h_statistics.get('mode_value', None),
            'last_24h_mode_values': last_24h_statistics.get('mode_values', None),
            'last_24h_range_value': last_24h_statistics.get('range_value', None),
            'last_24h_stedv_value': last_24h_statistics.get('stedv_value', None),
            'last_24h_variance_value': last_24h_statistics.get('variance_value', None),
            'last_24h_median_value': last_24h_statistics.get('median_value', None),
        }

        # For debugging purposes only.
        # print(statistics)

        # Save our unified statistics.
        instrument.statistics = statistics
        instrument.save()

        # For debugging purposes only.
        self.stdout.write(
            self.style.SUCCESS(_('%(dt)s | CIS | Finished running for instrument #%(id)s.') % {
                'dt': str(timezone.now()),
                'id': instrument_id
            })
        )

    def compute_statistics(self, instrument, aware_start_dt, aware_finish_dt):
        # For debugging purposes only.
        self.stdout.write(
            self.style.SUCCESS(_('%(dt)s | CIS | Processing from %(start_dt)s to %(finish_dt)s.') % {
                'dt': str(timezone.now()),
                'start_dt': str(aware_start_dt),
                'finish_dt': str(aware_finish_dt),
            })
        )

        # Run our code.
        data = TimeSeriesDatum.objects.filter(
            instrument=instrument,
            timestamp__range=[aware_start_dt, aware_finish_dt]
        ).order_by('value') # Invoice by value b/c we need to find the median.
        try:
            return self.get_statistics(instrument, aware_start_dt, aware_finish_dt, data)
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(_('%(dt)s | CIS | Failed generating statistics for date and time %(start_dt)s to %(finish_dt)s with reason:\n%(e)s') % {
                    'dt': str(timezone.now()),
                    'start_dt': str(aware_start_dt),
                    'finish_dt': str(aware_finish_dt),
                    'e': str(e)
                })
            )
            return {}

    def get_statistics(self, instrument, aware_start_dt, aware_finish_dt, data):
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
        For debugging purposes only.
        '''
        # print("MAX", max_value,"at",max_timestamp)
        # print("MIN", min_value,"at",min_timestamp)
        # print("MEAN", mean_value)
        # print("MEDIAN", median_value)
        # print("MODE VALUE", mode_value)
        # print("MODE VALUES", mode_values_array)
        # print("RANGE", range_value)
        # print("STEDV", stedv_value)
        # print("VAR", variance_value)

        '''
        Return our statistics.
        '''
        return {
            'min_value': min_value,
            'min_timestamp_utc': str(min_timestamp),
            'max_value': max_value,
            'max_timestamp_utc': str(max_timestamp),
            'mean_value': mean_value,
            'median_value': median_value,
            'mode_value': mode_value,
            'mode_values': mode_values_array,
            'range_value': range_value,
            'stedv_value': stedv_value,
            'variance_value': variance_value,
        }
