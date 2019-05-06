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
    absolute_url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = Device
        fields = (
            'slug',
            'name',
            'description',
            'uuid',
            'user',
            'type_of',
            'state',
            'data_interval_in_seconds',
            'created_at',
            'last_modified_at',
            'absolute_url'
        )


class DeviceInstrumentSerializer(serializers.ModelSerializer):
    absolute_url = serializers.ReadOnlyField(source='get_absolute_url')
    absolute_parent_url = serializers.ReadOnlyField(source='get_absolute_parent_url')
    unit_of_measure = serializers.ReadOnlyField(source='get_unit_of_measure')
    state = serializers.ReadOnlyField(source='get_pretty_state')
    last_measured_pretty_value = serializers.ReadOnlyField(source='get_pretty_last_measured_value')
    last_measured_pretty_at = serializers.ReadOnlyField(source='get_pretty_last_measured_at')
    slug = serializers.SlugField()
    timezone = serializers.ReadOnlyField(source='device.timezone')

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
            'timezone'
        )


class DeviceRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    uuid = serializers.ReadOnlyField()
    activated_at = serializers.ReadOnlyField()
    name = serializers.CharField(
        required=True,
        allow_blank=False,
    )
    description = serializers.CharField(
        required=True,
        allow_blank=False,
    )
    data_interval_in_seconds = serializers.IntegerField(
        required=True,
    )
    data_interval_in_minutes = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    slug = serializers.ReadOnlyField()
    absolute_url = serializers.ReadOnlyField(source='get_absolute_url')

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
            'name',
            'description',
            'data_interval_in_seconds',
            'data_interval_in_minutes',
            'state',
            'slug',
            'absolute_url',

            'last_measured_value',
            'last_measured_at',
            'last_measured_unit_of_measure',
            'last_measured_pretty_value',
            'last_measured_pretty_at',

            'humidity',
            'temperature',
        )

    def get_data_interval_in_minutes(self, obj):
        try:
            return obj.data_interval_in_seconds / 60.0
        except Exception as e:
            return None

    def get_state(self, obj):
        try:
            return obj.get_pretty_state()
        except Exception as e:
            return None

    def get_humidity(self, obj):
        try:
            humidity_instrument = obj.humidity_instrument
            s = DeviceInstrumentSerializer(humidity_instrument, many=False)
            return s.data
        except Exception as e:
            return None

    def get_temperature(self, obj):
        try:
            temperature_instrument = obj.temperature_instrument
            s = DeviceInstrumentSerializer(temperature_instrument, many=False)
            return s.data
        except Exception as e:
            return None


    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        # Get our context data.
        authenticated_user = self.context['authenticated_user']
        authenticated_user_from = self.context['authenticated_user_from']
        authenticated_user_from_is_public = self.context['authenticated_user_from_is_public']

        # Save our inputted & context data.
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.data_interval_in_seconds = validated_data.get('data_interval_in_seconds', instance.data_interval_in_seconds)
        instance.last_modified_by = authenticated_user
        instance.last_modified_from = authenticated_user_from
        instance.last_modified_from_is_public = authenticated_user_from_is_public
        instance.save()

        # instance.invoice.invalidate('total')
        return validated_data

    def delete(self, instance):
        instance.delete()



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
