# -*- coding: utf-8 -*-
import django_rq
from django_rq import job
from rq_scheduler import Scheduler
from datetime import datetime, timedelta
from django.apps import AppConfig
from django.conf import settings
from django.core.management import call_command

from foundation.models import User


@job
def run_instrument_alert_item_monitor_func():
    """
    Function will be called in the background runtime loop to handle iterating
    over all the instruments and performing our applications business logic on
    them.
    """
    from foundation.models import Instrument

    # DEVELOPERS NOTE:
    # (1) It is a business logic that users whom don't a subscription will not
    #     receive an alert.
    for instrument in Instrument.objects.filter(device__user__subscription_status=User.SUBSCRIPTION_STATUS.ACTIVE).iterator(chunk_size=250):
        call_command('instrument_alert_monitor', instrument.id, verbosity=0)


@job
def run_instrument_send_alert_email_func(alert_id):
    call_command('send_instrument_alert_email', alert_id, verbosity=0)


@job
def run_production_alert_item_monitor_func():
    """
    Function will be called in the background runtime loop to handle iterating
    over all the production objects and performing our applications business
    logic on them.
    """
    from foundation.models import Production

    # DEVELOPERS NOTE:
    # (1) It is a business logic that users whom don't a subscription will not
    #     receive an alert.
    for production in Production.objects.filter(state=Production.PRODUCTION_STATE.OPERATING, user__subscription_status=User.SUBSCRIPTION_STATUS.ACTIVE).iterator(chunk_size=250):
        call_command('production_alert_monitor', production.id, verbosity=0)


@job
def run_send_production_alert_email_func(alert_id):
    call_command('send_production_alert_email', alert_id, verbosity=0)
