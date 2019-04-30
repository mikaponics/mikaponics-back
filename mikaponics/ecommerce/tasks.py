# -*- coding: utf-8 -*-
import django_rq
from rq_scheduler import Scheduler
from datetime import datetime, timedelta
from django.apps import AppConfig
from django.conf import settings
from django.core.management import call_command


def run_send_customer_receipt_email_by_invoice_id_func(invoice_id):
    call_command('send_customer_receipt_email_by_order_id', invoice_id, verbosity=0)


def run_send_staff_receipt_email_by_invoice_id_func(invoice_id):
    call_command('send_staff_receipt_email_by_order_id', invoice_id, verbosity=0)


def run_process_stripe_event_by_id_func(event_id):
    call_command('process_stripe_event_by_id', event_id, verbosity=0)
