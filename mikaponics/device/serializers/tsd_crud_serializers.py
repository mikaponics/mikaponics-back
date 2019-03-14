# -*- coding: utf-8 -*-
import logging
import pytz
import time
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator

from foundation.models import Device, Instrument, TimeSeriesDatum
from foundation.model_resources import create_instrument_alert_in_system_if_possible

logger = logging.getLogger(__name__)


class TimeSeriesDatumCreateSerializer(serializers.Serializer):
    # Primary fields.
    instrument_uuid = serializers.UUIDField(required=True)
    value = serializers.FloatField(required=True)
    unix_timestamp = serializers.CharField(required=True, allow_blank=False)

    # Debugging information fields.
    # These fieldsa re useful for backend developers whom need to diagnose
    # the data in our API endpoint.
    utc_datetime = serializers.DateTimeField(read_only=True)
    local_datetime = serializers.DateTimeField(read_only=True)
    local_timezone = serializers.CharField(read_only=True)

    class Meta:
        fields = (
            'instrument_uuid',
            'type_of',
            'value',
            'unix_timestamp',
            'utc_datetime',
            'local_datetime',
            'local_timezone',
        )

    def validate(self, data):
        """
        Override the final validation to include additional extras. Any
        validation error will be populated in the "non_field_errors" field.
        """
        # Confirm that we have an assignment task open.
        instrument_uuid = data.get('instrument_uuid')
        unix_timestamp = data.get('unix_timestamp')

        # Validate `uuid` field.
        instrument = Instrument.objects.filter(uuid=instrument_uuid).first()
        if instrument is None:
            raise serializers.ValidationError(_("Please enter a valid `instrument_uuid` value."))

        # Validate `unix_timestamp` field.
        try:
            ts = int(unix_timestamp)
        except Exception as e:
            raise serializers.ValidationError(_("Please enter a valid `unix_timestamp` value."))

        now_ts = int(time.time())
        if ts > now_ts:
            raise serializers.ValidationError(_("Please enter a `unix_timestamp` value which is not in the future."))
        return data

    @transaction.atomic
    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        '''
        Get our inputs.
        '''
        # Get our context data.
        authenticated_user = self.context['authenticated_user']
        authenticated_user_from = self.context['authenticated_user_from']
        authenticated_user_from_is_public = self.context['authenticated_user_from_is_public']

        # Get user input.
        instrument_uuid = validated_data.get('instrument_uuid')
        value = validated_data.get('value')
        ts = int(validated_data.get('unix_timestamp'))

        '''
        Convert UTC to local timezone aware datetime.
        '''
        # Convert the timestamp to a timezone aware datetime value.
        naive_dt = datetime.fromtimestamp(ts)
        utc_aware_dt = naive_dt.replace(tzinfo=pytz.utc)

        # Fetch our hardware.
        instrument = Instrument.objects.select_for_update().get(uuid=instrument_uuid)

        # Convert to the instruments local timezone.
        local_timezone = pytz.timezone(instrument.device.timezone)
        local_aware_dt = utc_aware_dt.astimezone(local_timezone) # Convert to local timezone.

        '''
        Create datum object in database and update device & instrument.
        '''
        # Create our record.
        time_series_datum = TimeSeriesDatum.objects.create(
            instrument=instrument,
            value=value,
            timestamp=local_aware_dt
        )

        # Update our device / instrument with our latest record.
        instrument.set_last_recorded_datum(time_series_datum)
        instrument.device.set_last_recorded_datum(time_series_datum)

        # Update the device state and fill out our audit details.
        instrument.device.state = Device.DEVICE_STATE.ONLINE
        instrument.device.last_modified_by = authenticated_user
        instrument.device.last_modified_from = authenticated_user_from
        instrument.device.last_modified_from_is_public = authenticated_user_from_is_public
        instrument.device.save()
        instrument.last_modified_by = authenticated_user
        instrument.last_modified_from = authenticated_user_from
        instrument.last_modified_from_is_public = authenticated_user_from_is_public
        instrument.save()

        '''
        Create an alarm if possible.
        '''
        create_instrument_alert_in_system_if_possible(instrument, time_series_datum)

        '''
        Add our debugging information fields and return our validated data.
        '''
        validated_data['utc_datetime'] = str(utc_aware_dt)
        validated_data['local_datetime'] = str(local_aware_dt)
        validated_data['local_timezone'] = str(instrument.device.timezone)
        return validated_data


class TimeSeriesDataListSerializer(serializers.Serializer):
    instrument_uuid = serializers.UUIDField(source="instrument.uuid")
    value = serializers.FloatField()
    timestamp = serializers.DateTimeField()

    class Meta:
        fields = (
            'instrument_uuid',
            'value',
            'timestamp',
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'instrument',
        )
        return queryset
