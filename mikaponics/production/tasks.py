# -*- coding: utf-8 -*-
import django_rq
from rq_scheduler import Scheduler
from datetime import datetime, timedelta
from django.apps import AppConfig
from django.conf import settings
from django.core.management import call_command
from django.db.models import Q, Prefetch


def run_production_evaluation_handling_func():
    """
    Function will be called in the background runtime loop to handle iterating
    over all the production crops and evaluate a score.
    """
    from foundation.models import Production

    for production in Production.objects.iterator(chunk_size=250):
        call_command('evaluate_production_by_id', production.id, verbosity=0)
