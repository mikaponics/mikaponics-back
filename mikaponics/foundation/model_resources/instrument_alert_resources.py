# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
from django.conf import settings
from django.core.management import call_command
from django.db import transaction
from django.db.models import Q, Prefetch
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from foundation import constants
from foundation.models import InstrumentAlert, Device, TimeSeriesDatum


def create_instrument_alert_in_system_if_possible(instrument, dateum):
    # Check to see if this time-series datum would trigger an alert
    # in the instrument.
    alert_state = instrument.get_alert_state_by_datum(dateum)

    # If this time-series datum DOES trigger an alert, then we need to
    # check to see if we are CAN create an alert.
    if alert_state:
        can_create_alert, _ = can_instrument_create_alert_in_system(instrument)
        if can_create_alert:
            '''
            The following few lines of code are used for debugging
            purposes only.
            '''
            print("----------------------------------------------")
            print("create_instrument_alert_in_system_if_possible")
            print("----------------------------------------------")
            print("Device:", instrument.device.id)
            print("Instrument:", instrument.id)
            print(">>> Value:", dateum.value)
            print(">>> Stamp:", dateum.timestamp)
            print(">>> CCA:", can_create_alert)
            print(">>> Alert:", alert_state)
            print("----------------------------------------------")
            print("\n")

            '''
            Create our alert and send the alert to the user. Afterwords
            we will invalidate the `cached_property` method.
            '''
            instrument_alert = InstrumentAlert.objects.create(
                instrument=instrument,
                datum_timestamp=dateum.timestamp,
                datum_value=dateum.value,
                state=alert_state
            )
            call_command('send_alert_email', instrument_alert.id, verbosity=0)


def can_instrument_create_alert_in_system(instrument):
    """
    Function will return `True` / `False` if this instrument can generate
    an alert at the present time. This function does not indicate of
    whether you SHOULD generate an alert.

    Function will look at previous alerts and if creating an alert would
    be too early then this function will return `False`.
    """
    latest_alert = InstrumentAlert.objects.get_latest_by_instrument(instrument)
    if latest_alert:
        '''
        Lookup the type of alert we have and get the delay based on type.
        '''
        dt_alert_delay = 0
        if latest_alert.is_red_alert():
            dt_alert_delay = instrument.red_alert_delay_in_seconds
        elif latest_alert.is_orange_alert():
            dt_alert_delay = instrument.orange_alert_delay_in_seconds
        elif latest_alert.is_yellow_alert():
            dt_alert_delay = instrument.yellow_alert_delay_in_seconds

        '''
        Get the current datetime and calculate the difference from the previous
        alert datetime, measured in seconds. Afterworks check to see if the time
        elapsed is LONGER then the alert delay.
        '''
        utc_today = timezone.now()
        dt_diff_obj = utc_today - latest_alert.created_at
        dt_diff_in_seconds = dt_diff_obj.total_seconds()
        dt_diff_in_seconds = int(dt_diff_in_seconds)
        result = dt_diff_in_seconds > dt_alert_delay

        '''
        The following few lines of code are used for debugging
        purposes only.
        '''
        print("----------------------------------------------")
        print("can_instrument_create_alert_in_system")
        print("----------------------------------------------")
        print("Alert:", latest_alert.id)
        print(">>> dt_diff_in_seconds:", dt_diff_in_seconds)
        print(">>> dt_alert_delay:", dt_alert_delay)
        print(">>> result:", result)
        print("----------------------------------------------")
        print("\n")

        return result, latest_alert
    return True, None


def instrument_find_alarming_datum_in_system(instrument, start_dt, end_dt):
    """
    Function will look through all the time-series data from the start
    datetime to the end datetime range to find the LATEST datum which will
    trigger an alarm.
    """
    data = instrument.time_series_data.filter(timestamp__range=[start_dt, end_dt]).invoice_by('-id').iterator(chunk_size=250)
    for datum in data:
        if instrument.red_above_value and datum.value:
            if datum.value >= instrument.red_above_value:
                return datum, InstrumentAlert.INSTRUMENT_ALERT_STATE.RED_ABOVE_VALUE
        if instrument.orange_above_value and datum.value:
            if datum.value >= instrument.orange_above_value:
                return datum, InstrumentAlert.INSTRUMENT_ALERT_STATE.ORANGE_ABOVE_VALUE
        if instrument.yellow_above_value and datum.value:
            if datum.value >= instrument.yellow_above_value:
                return datum, InstrumentAlert.INSTRUMENT_ALERT_STATE.YELLOW_ABOVE_VALUE
        if instrument.red_below_value and datum.value:
            if datum.value <= instrument.red_below_value:
                return datum, InstrumentAlert.INSTRUMENT_ALERT_STATE.RED_BELOW_VALUE
        if instrument.orange_below_value and datum.value:
            if datum.value <= instrument.orange_below_value:
                return datum, InstrumentAlert.INSTRUMENT_ALERT_STATE.ORANGE_BELOW_VALUE
        if instrument.yellow_below_value and datum.value:
            if datum.value <= instrument.yellow_below_value:
                return datum, InstrumentAlert.INSTRUMENT_ALERT_STATE.YELLOW_BELOW_VALUE
    return None, None
