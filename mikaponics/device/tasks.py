import requests
import logging
from rq import get_current_job
from django_rq import job
from django.core.management import call_command


logger = logging.getLogger(__name__)


@job
def run_devices_handling_func():
    """
    Function will be called in the background runtime loop to handle iterating
    over all the devices and performing our applications business logic on
    them.
    """
    from foundation.models import Device

    for device in Device.objects.iterator(chunk_size=250):
        call_command('check_devices',device.id,verbosity=0)


@job
def run_check_devices_func(device_id):
    call_command(
        'check_devices',
        device_id,
        verbosity=0
    )


@job
def run_device_simulators_func():
    """
    Function used to simulate device in our system.
    """
    from foundation.models import Device, DeviceSimulator

    for deviceSimulator in DeviceSimulator.objects.filter(is_running=True).iterator(chunk_size=250):
        for instrument in deviceSimulator.device.instruments.all():
            if instrument.simulator:
                call_command('instrument_simulator_tick', instrument.simulator.id, verbosity=0)
