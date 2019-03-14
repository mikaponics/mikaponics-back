from foundation.models import Device
from foundation.models import Instrument


def get_device_configuration_data(device):
    """
    Function will generate the environemnt variable configuration data for this
    device based on what type of device this is.
    """
    # If the humidity sensor was attached then lets add our configuration
    # informatin for it.

    humidity_instrument = device.instruments.filter(type_of=Instrument.INSTRUMENT_TYPE.HUMIDITY).first()
    humidity_configuration = {}
    if humidity_instrument:
        humidity_configuration = humidity_instrument.configuration
        humidity_configuration['uuid'] = humidity_instrument.uuid

    temperature_instrument = device.instruments.filter(type_of=Instrument.INSTRUMENT_TYPE.TEMPERATURE).first()
    temperature_configuration = {}
    if temperature_instrument:
        temperature_configuration = temperature_instrument.configuration
        temperature_configuration['uuid'] = temperature_instrument.uuid

    # Generate our configuration data based on the "LOGGER" device type.
    return {
        "data_interval_in_minutes": device.data_interval_in_minutes,
        "humidity": humidity_configuration,
        "temperature": temperature_configuration,
    }
