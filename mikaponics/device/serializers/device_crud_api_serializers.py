# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response

from foundation.models import Device, Instrument, User


class DeviceListCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=User.objects.all(),
        allow_null=False,
    )
    type_of = serializers.IntegerField(required=False, allow_null=True)
    state = serializers.IntegerField(required=False, allow_null=True)
    data_interval_in_seconds = serializers.CharField(
        required=True,
        allow_blank=False,
    )
    created_at = serializers.DateTimeField(read_only=True)
    last_modified_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Device
        fields = (
            'uuid',
            'user',
            'type_of',
            'state',
            'data_interval_in_seconds',
            'created_at',
            'last_modified_at',
        )


class DeviceInstrumentSerializer(serializers.ModelSerializer):
    uuid = serializers.ReadOnlyField()
    unit_of_measure = serializers.ReadOnlyField(source='get_unit_of_measure')

    class Meta:
        model = Instrument
        fields = (
            'uuid',
            'last_measured_value',
            'last_measured_timestamp',
            'unit_of_measure',
        )


class DeviceRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    uuid = serializers.ReadOnlyField()
    activated_at = serializers.ReadOnlyField()
    data_interval_in_seconds = serializers.IntegerField(
        required=True,
    )
    data_interval_in_minutes = serializers.SerializerMethodField()
    statistics = serializers.JSONField(read_only=True)
    state = serializers.SerializerMethodField()

    last_measured_value = serializers.SerializerMethodField()
    last_measured_timestamp = serializers.SerializerMethodField()
    last_measured_instrument_type_of = serializers.SerializerMethodField()
    last_measured_instrument_id = serializers.SerializerMethodField()
    last_measured_unit_of_measure = serializers.SerializerMethodField()

    humidity_last_measured_value = serializers.SerializerMethodField()
    humidity_last_measured_timestamp = serializers.SerializerMethodField()
    humidity_unit_of_measure = serializers.SerializerMethodField()

    temperature_last_measured_value = serializers.SerializerMethodField()
    temperature_last_measured_timestamp = serializers.SerializerMethodField()
    temperature_unit_of_measure = serializers.SerializerMethodField()

    class Meta:
        model = Device
        fields = (
            'uuid',
            'activated_at',
            'timezone',
            'data_interval_in_seconds',
            'data_interval_in_minutes',
            'statistics',
            'state',
            'last_measured_value',
            'last_measured_timestamp',
            'last_measured_unit_of_measure',
            'last_measured_instrument_type_of',
            'last_measured_instrument_id',
            'humidity_last_measured_value',
            'humidity_last_measured_timestamp',
            'humidity_unit_of_measure',
            'temperature_last_measured_value',
            'temperature_last_measured_timestamp',
            'temperature_unit_of_measure'
        )

    def get_data_interval_in_minutes(self, obj):
        return obj.data_interval_in_seconds / 60.0

    def get_state(self, obj):
        return obj.get_pretty_state()

    def get_last_measured_value(self, obj):
        return obj.last_measured_value

    def get_last_measured_timestamp(self, obj):
        return obj.last_measured_timestamp

    def get_last_measured_unit_of_measure(self, obj):
        return obj.last_measured_unit_of_measure;

    def get_last_measured_instrument_type_of(self, obj):
        instrument = obj.last_measured_instrument
        return instrument.get_pretty_instrument_type_of()

    def get_last_measured_instrument_id(self, obj):
        instrument = obj.last_measured_instrument
        return instrument.id

    def get_humidity(self, obj):
        humidity_instrument = obj.humidity_instrument
        s = DeviceInstrumentSerializer(humidity_instrument, many=False)
        return s.data

    def get_temperature(self, obj):
        temperature_instrument = obj.temperature_instrument
        s = DeviceInstrumentSerializer(temperature_instrument, many=False)
        return s.data


class DeviceProfileSerializer(serializers.ModelSerializer):

    name = serializers.CharField(
        required=True,
        allow_blank=False,
    )
    description = serializers.CharField(
        required=True,
        allow_blank=False,
    )

    class Meta:
        model = Device
        fields = (
            'name',
            'description',
        )
