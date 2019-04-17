# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.exceptions import SuspiciousOperation
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from oauth2_provider.models import (
    Application,
    AbstractApplication,
    AbstractAccessToken,
    AccessToken,
    RefreshToken
)

from foundation import constants
from foundation.mixins import MikaponicsListView, MikaponicsDetailView
from foundation.models import Device, Instrument


class DeviceEnvironmentVariablesFileView(LoginRequiredMixin, MikaponicsDetailView):
    """
    Class view used to create the contents of the `environment variable` file
    which will be used in the `.env` file for the ``mikapod`` device.
    """
    context_object_name = 'device'
    model = Device
    template_name = 'device/environment_variable/detail_view.html'
    menu_id = "device"

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Defensive Code (1): Ensure oAuth 2.0 is setup properly.
        try:
            application = Application.objects.get(name=self.object.uuid)
        except Application.DoesNotExist:
            # You need to create an application via
            # `/admin/oauth2_provider/application/add/`
            # with :
            # (1) Client type: Confidential
            # (2) Authorization grant type: Client credentials
            # (3) Name: <Use the UUID of the device>.
            # (4) Skip authorization: True
            raise SuspiciousOperation("Invalid request - must create an oAuth 2.0 Application.")

        # Defensive Code (2): Ensure the insturments are setup properly.
        try:
            humidity = Instrument.objects.get(
                device=self.object,
                type_of=Instrument.INSTRUMENT_TYPE.HUMIDITY
            )
        except Instrument.DoesNotExist:
            raise SuspiciousOperation("Invalid request - must create humidity instrument.")
        try:
            temperature = Instrument.objects.get(
                device=self.object,
                type_of=Instrument.INSTRUMENT_TYPE.TEMPERATURE
            )
        except Instrument.DoesNotExist:
            raise SuspiciousOperation("Invalid request - must create temperature instrument.")

        #-------------------------------#
        # API WEB-SERVICE CONFIGURATION #
        #-------------------------------#
        aURL = settings.MIKAPONICS_BACKEND_HTTP_PROTOCOL
        aURL += settings.MIKAPONICS_BACKEND_HTTP_DOMAIN
        modified_context['WEB_SERVICE_URL'] = aURL
        modified_context['WEB_SERVICE_CLIENT_ID'] = application.client_id
        modified_context['WEB_SERVICE_CLIENT_SECRET'] = application.client_secret
        modified_context['WEB_SERVICE_DEVICE_UUID'] = self.object.uuid

        #---------------------------#
        # APPLICATION CONFIGURATION #
        #---------------------------#
        modified_context['DATABASE'] = "storage.db"
        modified_context['MAINLOOP_RUNTIME_SLEEP_INTERVAL_IN_SECONDS'] = 1
        modified_context['MAINLOOP_ERROR_SLEEP_INTERVAL_IN_SECONDS'] = 15
        modified_context['ACTIVATION_OPERATION_SLEEP_INTERVAL_IN_SECONDS'] = 1
        modified_context['SETUP_INSTRUMENTS_OPERATION_SLEEP_INTERVAL_IN_SECONDS'] = 1
        modified_context['DATA_UPLOADER_OPERATION_SLEEP_INTERVAL_IN_SECONDS'] = 1
        modified_context['LOCAL_TIMEZONE_NAME'] = "America/Toronto"

        #----------------------#
        # DEVICE CONFIGURATION #
        #----------------------#
        modified_context['HUMIDITY_SERIAL_NUMBER'] = humidity.configuration['serial_number']
        modified_context['HUMIDITY_VINT_HUB_PORT_NUMBER'] = humidity.configuration['hub_port_number']
        modified_context['HUMIDITY_CHANNEL_NUMBER'] = humidity.configuration['channel_number']
        modified_context['TEMPERATURE_SERIAL_NUMBER'] = temperature.configuration['serial_number']
        modified_context['TEMPERATURE_VINT_HUB_PORT_NUMBER'] = temperature.configuration['hub_port_number']
        modified_context['TEMPERATURE_CHANNEL_NUMBER'] = temperature.configuration['channel_number']

        # Return our modified context.
        return modified_context
