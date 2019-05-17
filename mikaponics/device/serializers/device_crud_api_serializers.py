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
    slug = serializers.SlugField(required=False, allow_blank=True, allow_null=True)
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
    tvoc = serializers.SerializerMethodField()
    co2 = serializers.SerializerMethodField()
    air_pressure = serializers.SerializerMethodField()
    altitude = serializers.SerializerMethodField()
    water_level = serializers.SerializerMethodField()
    power_usage = serializers.SerializerMethodField()
    ph = serializers.SerializerMethodField()
    ec = serializers.SerializerMethodField()
    orp = serializers.SerializerMethodField()
    camera = serializers.SerializerMethodField()
    heat_vision = serializers.SerializerMethodField()
    uv_light = serializers.SerializerMethodField()
    triad_spectroscopy = serializers.SerializerMethodField()


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
            'tvoc',
            'co2',
            'air_pressure',
            'altitude',
            'water_level',
            'ph',
            'ec',
            'orp',
            'power_usage',
            'camera',
            'heat_vision',
            'uv_light',
            'triad_spectroscopy',
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
            if humidity_instrument:
                s = DeviceInstrumentSerializer(humidity_instrument, many=False)
                return s.data
        except Exception as e:
            print("DeviceRetrieveUpdateDestroySerializer | get_humidity |", e)
        return None

    def get_temperature(self, obj):
        try:
            temperature_instrument = obj.temperature_instrument
            if temperature_instrument:
                s = DeviceInstrumentSerializer(temperature_instrument, many=False)
                return s.data
        except Exception as e:
            print("DeviceRetrieveUpdateDestroySerializer | get_temperature |", e)
        return None

    def get_tvoc(self, obj):
        try:
            tvoc_instrument = obj.tvoc_instrument
            if tvoc_instrument:
                s = DeviceInstrumentSerializer(tvoc_instrument, many=False)
                return s.data
        except Exception as e:
            print("DeviceRetrieveUpdateDestroySerializer | get_tvoc |", e)
        return None

    def get_co2(self, obj):
        try:
            co2_instrument = obj.co2_instrument
            if co2_instrument:
                s = DeviceInstrumentSerializer(co2_instrument, many=False)
                return s.data
        except Exception as e:
            print("DeviceRetrieveUpdateDestroySerializer | get_co2 |", e)
        return None

    def get_air_pressure(self, obj):
        try:
            air_pressure_instrument = obj.air_pressure_instrument
            if air_pressure_instrument:
                s = DeviceInstrumentSerializer(air_pressure_instrument, many=False)
                return s.data
        except Exception as e:
            print("DeviceRetrieveUpdateDestroySerializer | get_air_pressure |", e)
        return None

    def get_altitude(self, obj):
        try:
            altitude_instrument = obj.altitude_instrument
            if altitude_instrument:
                s = DeviceInstrumentSerializer(altitude_instrument, many=False)
                return s.data
        except Exception as e:
            print("DeviceRetrieveUpdateDestroySerializer | get_altitude |", e)
        return None

    def get_water_level(self, obj):
        try:
            water_level_instrument = obj.water_level_instrument
            if water_level_instrument:
                s = DeviceInstrumentSerializer(water_level_instrument, many=False)
                return s.data
        except Exception as e:
            print("DeviceRetrieveUpdateDestroySerializer | get_altitude |", e)
        return None

    def get_ph(self, obj):
        try:
            ph_instrument = obj.ph_instrument
            if ph_instrument:
                s = DeviceInstrumentSerializer(ph_instrument, many=False)
                return s.data
        except Exception as e:
            print("DeviceRetrieveUpdateDestroySerializer | get_ph |", e)
        return None

    def get_ec(self, obj):
        try:
            ec_instrument = obj.ec_instrument
            if ec_instrument:
                s = DeviceInstrumentSerializer(ec_instrument, many=False)
                return s.data
        except Exception as e:
            print("DeviceRetrieveUpdateDestroySerializer | get_ec |", e)
        return None

    def get_orp(self, obj):
        try:
            orp_instrument = obj.orp_instrument
            if orp_instrument:
                s = DeviceInstrumentSerializer(orp_instrument, many=False)
                return s.data
        except Exception as e:
            print("DeviceRetrieveUpdateDestroySerializer | get_orp |", e)
        return None

    def get_power_usage(self, obj):
        try:
            power_usage_instrument = obj.power_usage_instrument
            if power_usage_instrument:
                s = DeviceInstrumentSerializer(power_usage_instrument, many=False)
                return s.data
        except Exception as e:
            print("DeviceRetrieveUpdateDestroySerializer | get_power_usage |", e)
        return None

    def get_camera(self, obj):
        try:
            power_usage_instrument = obj.camera_instrument
            if power_usage_instrument:
                s = DeviceInstrumentSerializer(power_usage_instrument, many=False)
                return s.data
        except Exception as e:
            print("DeviceRetrieveUpdateDestroySerializer | get_camera |", e)
        return None

    def get_heat_vision(self, obj):
        try:
            heat_vision_instrument = obj.heat_vision_instrument
            if heat_vision_instrument:
                s = DeviceInstrumentSerializer(heat_vision_instrument, many=False)
                return s.data
        except Exception as e:
            print("DeviceRetrieveUpdateDestroySerializer | get_heat_vision |", e)
        return None

    def get_uv_light(self, obj):
        try:
            uv_light_instrument = obj.uv_light_instrument
            if uv_light_instrument:
                s = DeviceInstrumentSerializer(uv_light_instrument, many=False)
                return s.data
        except Exception as e:
            print("DeviceRetrieveUpdateDestroySerializer | get_uv_light |", e)
        return None

    def get_triad_spectroscopy(self, obj):
        try:
            triad_spectroscopy_instrument = obj.triad_spectroscopy_instrument
            if triad_spectroscopy_instrument:
                s = DeviceInstrumentSerializer(triad_spectroscopy_instrument, many=False)
                return s.data
        except Exception as e:
            print("DeviceRetrieveUpdateDestroySerializer | get_uv_light |", e)
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
