# -*- coding: utf-8 -*-
import django_rq
from django_rq import job
from rq_scheduler import Scheduler
from datetime import datetime, timedelta
from django.apps import AppConfig
from django.conf import settings
from django.core.management import call_command
from django.db.models import Q, Prefetch


@job
def run_instruments_handling_func():
    """
    Function will be called in the background runtime loop to handle iterating
    over all the instruments and performing our applications business logic on
    them.
    """
    from foundation.models import Instrument

    for instrument in Instrument.objects.iterator(chunk_size=250):
        call_command('compute_instrument_statistics', instrument.id, verbosity=0)


@job
def run_instrument_simulators_func():
    """
    Function used to simulate instruments in our system.
    """
    from foundation.models import Instrument, InstrumentSimulator

    for simulator in InstrumentSimulator.objects.filter(
        Q(is_running=True)&
        ~Q(instrument__type_of=Instrument.INSTRUMENT_TYPE.POWER_USAGE)
    ).iterator(chunk_size=250):
        call_command('instrument_simulator_tick', simulator.id, verbosity=0)


@job
def run_power_usage_instrument_simulators_func():
    """
    Function used to simulate "power usage" instrument.
    """
    from foundation.models import Instrument, InstrumentSimulator

    for simulator in InstrumentSimulator.objects.filter(
        Q(is_running=True)&
        Q(instrument__type_of=Instrument.INSTRUMENT_TYPE.POWER_USAGE)
    ).iterator(chunk_size=250):
        call_command('instrument_simulator_tick', simulator.id, verbosity=0)
