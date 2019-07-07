# -*- coding: utf-8 -*-
import django_rq
from rq_scheduler import Scheduler
from datetime import datetime, timedelta
from django.apps import AppConfig
from django.conf import settings
from django.core.management import call_command
from django.utils import timezone


class InstrumentConfig(AppConfig):
    """
    Class will load up the background processes, powered by `rq-scheduler`
    library, to run for this app.
    """
    name = 'instrument'
    verbose_name = 'Instrument'

    def ready(self):
        """
        On django runtime, load up the following code.
        """
        # Load our tasks when this app finished loading and is ready.
        from instrument.tasks import (
            run_instruments_handling_func,
            run_instrument_simulators_func,
            run_power_usage_instrument_simulators_func
        )

        scheduler = django_rq.get_scheduler('default')

        # Delete previously loaded ETLs.
        for job in scheduler.get_jobs():
            if "instrument" in str(job): # Only delete jobs belonging to this app.
                job.delete()

        # Variable used to track the maximum number of minutes the ETL can
        # run before it's considered an error and needs to stop the ETL.
        timeout = timedelta(minutes=666)

        # Pick a start date in the future.
        start_dt = timezone.now()
        start_dt = start_dt + timedelta(minutes=1)
        start_dt = start_dt.replace(second=0, microsecond=0)

        # Run our background process.
        scheduler.schedule(
            scheduled_time=start_dt,             # Time for first execution, in UTC timezone
            func=run_instruments_handling_func,  # Function to be queued
            args=[],                             # Arguments passed into function when executed
            kwargs={},                           # Keyword arguments passed into function when executed
            interval=60,                         # Time before the function is called again, in seconds
            repeat=None,                         # Repeat this number of times (None means repeat forever)
            meta={'type': 'instrument'},         # Arbitrary pickleable data on the job itself
            timeout=timeout.seconds              # Automatically terminate process if exceeds this time.
        )
        scheduler.schedule(
            scheduled_time=start_dt,             # Time for first execution, in UTC timezone
            func=run_instrument_simulators_func, # Function to be queued
            args=[],                             # Arguments passed into function when executed
            kwargs={},                           # Keyword arguments passed into function when executed
            interval=60,                         # Time before the function is called again, in seconds
            repeat=None,                         # Repeat this number of times (None means repeat forever)
            meta={'type': 'instrument'},         # Arbitrary pickleable data on the job itself
            timeout=timeout.seconds              # Automatically terminate process if exceeds this time.
        )
        scheduler.schedule( # Execute once per hour
            scheduled_time=start_dt,             # Time for first execution, in UTC timezone
            func=run_power_usage_instrument_simulators_func, # Function to be queued
            args=[],                             # Arguments passed into function when executed
            kwargs={},                           # Keyword arguments passed into function when executed
            interval=3600,                       # Time before the function is called again, in seconds
            repeat=None,                         # Repeat this number of times (None means repeat forever)
            meta={'type': 'instrument'},         # Arbitrary pickleable data on the job itself
            timeout=timeout.seconds              # Automatically terminate process if exceeds this time.
        )
