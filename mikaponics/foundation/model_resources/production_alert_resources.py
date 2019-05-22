# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
from django.conf import settings
from django.core.management import call_command
from django.db import transaction
from django.db.models import Q, Prefetch
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from foundation import constants
from foundation.models import Device, TimeSeriesDatum
from foundation.models.alert_item import AlertItem


def create_production_alert_item_in_system_if_possible(production):
    """
    Function will take the inputted parameter and see if the `Production` object
    needs to have an alert generated.
    """
    # STEP 1:
    # Check to see if an alert SHOULD be created.
    if production.alert_below_value:

        # STEP 2:
        # Check to see if an alert CAN be created.
        should_alert = production.evaluation_score <= production.alert_below_value
        if should_alert:
            can_create_alert, previous_alert = can_production_alert_create_alert_in_system(production)
            if can_create_alert:
                '''
                The following few lines of code are used for debugging
                purposes only.
                '''
                print("--------------------------------------------------")
                print("create_production_alert_item_in_system_if_possible")
                print("--------------------------------------------------")
                print("Production:", production.slug)
                print(">>> Previous Alert DT:", previous_alert.created_at)
                print(">>> Curent System DT:", timezone.now())
                print(">>> Evaluation Score:", production.evaluation_score)
                print(">>> Alert Below Value:", production.alert_below_value)
                print(">>> Can Create Alert:", can_create_alert)
                print("----------------------------------------------")
                print("\n")

                '''
                Create our alert and send the alert to the user. Afterwords
                we will invalidate the `cached_property` method.
                '''
                return AlertItem.objects.create(
                    user=production.user,
                    type_of=AlertItem.ALERT_TYPE_OF.PRODUCTION,
                    production=production,
                    timestamp=production.last_modified_at,
                    value=production.evaluation_score,
                    state=AlertItem.ALERT_ITEM_STATE.UNREAD,
                    condition=AlertItem.ALERT_ITEM_CONDITION.RED_BELOW_VALUE
                )
    return None


def can_production_alert_create_alert_in_system(production):
    """
    Function will return `True` / `False` if this alert can generate
    an alert at the present time. This function does not indicate of
    whether you SHOULD generate an alert.

    Function will look at previous alerts in the database and check if
    creating an alert would be too early then this function will return `False`.
    """
    latest_alert = AlertItem.objects.get_latest_by_production(production)
    if latest_alert:
        dt_alert_delay = production.alert_delay_in_seconds

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
        print("can_alert_create_alert_in_system")
        print("----------------------------------------------")
        print("Alert:", latest_alert.id)
        print(">>> dt_diff_in_seconds:", dt_diff_in_seconds)
        print(">>> dt_alert_delay:", dt_alert_delay)
        print(">>> can create:", result)
        print("----------------------------------------------")
        print("\n")

        return result, latest_alert
    return True, None
