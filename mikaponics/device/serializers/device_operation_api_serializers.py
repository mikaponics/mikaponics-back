# -*- coding: utf-8 -*-
import logging
import pytz
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
from foundation.model_resources import get_device_configuration_data


logger = logging.getLogger(__name__)


class DeviceActivateOperationSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(required=True)
    activated_at = serializers.DateTimeField(read_only=True)
    configuration = serializers.JSONField(read_only=True)

    class Meta:
        fields = (
            'uuid',
            'activated_at',
            'configuration',
        )

    def validate(self, data):
        """
        Override the final validation to include additional extras. Any
        validation error will be populated in the "non_field_errors" field.
        """
        # Confirm that we have an assignment task open.
        uuid = data['uuid']
        if uuid is None:
            raise serializers.ValidationError(_("Invalid UUID."))
        return data

    @transaction.atomic
    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        # Get user input.
        uuid = validated_data['uuid']

        # Activate our device.
        device = Device.objects.get(uuid=uuid)
        device.activated_at = timezone.now()
        device.last_modified_by = self.context.get('authenticate_user')
        device.last_modified_from = self.context.get('authenticate_user_from')
        device.last_modified_from_is_public = self.context.get('authenticate_user_from_is_public')
        device.save()

        validated_data['activated_at'] = device.activated_at
        validated_data['configuration'] = get_device_configuration_data(device)
        return validated_data


class DeviceInstrumentSetTimeSeriesDatumeOperationSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(required=True)
    type_of = serializers.IntegerField(required=True)
    value = serializers.FloatField(required=True)
    utc_timestamp = serializers.CharField(required=True, allow_blank=False)
    system_status = serializers.CharField(read_only=True)

    class Meta:
        fields = (
            'uuid',
            'type_of',
            'value',
            'utc_timestamp',
        )

    def validate(self, data):
        """
        Override the final validation to include additional extras. Any
        validation error will be populated in the "non_field_errors" field.
        """
        # Confirm that we have an assignment task open.
        uuid = data.get('uuid')
        type_of = data.get('type_of')
        utc_timestamp = data.get('utc_timestamp')

        # Validate `uuid` field.
        device = Device.objects.filter(uuid=uuid).first()
        if device is None:
            raise serializers.ValidationError(_("Please enter a valid `uuid` value."))

        # Validate `instrument` field.
        instrument = device.instruments.filter(type_of=type_of).first()
        if instrument is None:
            raise serializers.ValidationError(_("Please enter a valid `type_of` value."))

        # Validate `utc_timestamp` field.
        try:
            ts = int(utc_timestamp)
        except Exception as e:
            raise serializers.ValidationError(_("Please enter a valid `utc_timestamp` value."))
        dt = datetime.fromtimestamp(ts)
        if dt > datetime.utcnow():
            raise serializers.ValidationError(_("Please enter a `utc_timestamp` value which is not in the future."))
        return data

    @transaction.atomic
    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        # Get user input.
        uuid = validated_data.get('uuid')
        type_of = validated_data.get('type_of')
        value = validated_data.get('value')
        ts = int(validated_data.get('utc_timestamp'))
        dt = datetime.fromtimestamp(ts)
        aware_dt = dt.replace(tzinfo=pytz.utc)

        # Fetch our hardware.
        device = Device.objects.get(uuid=uuid)
        instrument = device.instruments.get(type_of=type_of)

        # Create our record.
        time_series_datume = TimeSeriesDatum.objects.create(
            instrument=instrument,
            value=value,
            timestamp=aware_dt
        )

        # validated_data['activated_at'] = device.activated_at
        validated_data['system_status'] = 'received'
        return validated_data
