# -*- coding: utf-8 -*-
import django_rq
from rq_scheduler import Scheduler
from datetime import datetime, timedelta
from django.apps import AppConfig
from django.conf import settings
from django.core.management import call_command


# def run_alert_item_monitor_func():
#     """
#     Function will be called in the background runtime loop to handle iterating
#     over all the instruments and performing our applications business logic on
#     them.
#     """
#     from foundation.models import Instrument
#
#     for instrument in Instrument.objects.iterator(chunk_size=250):
#         call_command('alert_item_monitor', instrument.id, verbosity=0)
#
#
# def run_send_alert_email(instrument_id):
#     call_command('send_alert_email', instrument_id, verbosity=0)
