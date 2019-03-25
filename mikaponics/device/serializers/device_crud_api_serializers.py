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
    absolute_url = serializers.ReadOnlyField(source='get_absolute_url')
    absolute_parent_url = serializers.ReadOnlyField(source='get_absolute_parent_url')
    unit_of_measure = serializers.ReadOnlyField(source='get_unit_of_measure')
    state = serializers.ReadOnlyField(source='get_pretty_state')
    last_measured_pretty_value = serializers.ReadOnlyField(source='get_pretty_last_measured_value')
    last_measured_pretty_at = serializers.ReadOnlyField(source='get_pretty_last_measured_at')
    slug = serializers.SlugField()

    class Meta:
        model = Instrument
        fields = (
            'absolute_url',
            'absolute_parent_url',
            'last_measured_value',
            'last_measured_at',
            'unit_of_measure',
            'last_measured_pretty_value',
            'last_measured_pretty_at',
            'state',
            'slug',
        )


class DeviceRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    uuid = serializers.ReadOnlyField()
    activated_at = serializers.ReadOnlyField()
    data_interval_in_seconds = serializers.IntegerField(
        required=True,
    )
    data_interval_in_minutes = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    slug = serializers.ReadOnlyField()

    last_measured_pretty_value = serializers.ReadOnlyField(source='get_pretty_last_measured_value')
    last_measured_pretty_at = serializers.ReadOnlyField(source='get_pretty_last_measured_at')

    humidity = serializers.SerializerMethodField()
    temperature = serializers.SerializerMethodField()

    class Meta:
        model = Device
        fields = (
            'uuid',
            'activated_at',
            'timezone',
            'data_interval_in_seconds',
            'data_interval_in_minutes',
            'state',
            'slug',

            'last_measured_value',
            'last_measured_at',
            'last_measured_unit_of_measure',
            'last_measured_pretty_value',
            'last_measured_pretty_at',

            'humidity',
            'temperature',
        )

    def get_data_interval_in_minutes(self, obj):
        return obj.data_interval_in_seconds / 60.0

    def get_state(self, obj):
        return obj.get_pretty_state()

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
