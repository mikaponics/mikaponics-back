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

from foundation.models import AlertItem


class AlertItemListSerializer(serializers.ModelSerializer):

    state = serializers.SerializerMethodField()
    device_name = serializers.CharField(read_only=True, source="instrument.device.name")
    device_slug = serializers.SlugField(read_only=True, source="instrument.device.slug")
    device_timezone = serializers.SlugField(read_only=True, source="instrument.device.timezone")
    device_absolute_url = serializers.SlugField(read_only=True, source="instrument.device.get_absolute_url")
    instrument_type = serializers.CharField(read_only=True, source="instrument.get_pretty_instrument_type_of")
    instrument_slug = serializers.SlugField(read_only=True, source="instrument.slug")
    instrument_absolute_url = serializers.SlugField(read_only=True, source="instrument.get_absolute_url")
    instrument_unit_of_measure = serializers.CharField(read_only=True, source="instrument.get_unit_of_measure", allow_null=True)
    icon = serializers.CharField(read_only=True, source="get_icon")
    absolute_url = serializers.CharField(read_only=True, source="get_absolute_url")

    class Meta:
        model = AlertItem
        fields = (
            'device_name',
            'device_slug',
            'device_timezone',
            'device_absolute_url',
            'instrument_type',
            'instrument_slug',
            'instrument_absolute_url',
            'instrument_unit_of_measure',
            'datum_timestamp',
            'datum_value',
            'state',
            'created_at',
            'icon',
            'absolute_url',
        )

    def get_state(self, obj):
        return obj.get_pretty_state()

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'instrument',
            'instrument__device',
        )
        return queryset


class AlertItemRetrieveSerializer(serializers.ModelSerializer):

    state = serializers.SerializerMethodField()
    device_name = serializers.CharField(read_only=True, source="instrument.device.name")
    device_slug = serializers.SlugField(read_only=True, source="instrument.device.slug")
    device_timezone = serializers.SlugField(read_only=True, source="instrument.device.timezone")
    device_absolute_url = serializers.SlugField(read_only=True, source="instrument.device.get_absolute_url")
    instrument_type = serializers.CharField(read_only=True, source="instrument.get_pretty_instrument_type_of")
    instrument_slug = serializers.SlugField(read_only=True, source="instrument.slug")
    instrument_absolute_url = serializers.SlugField(read_only=True, source="instrument.get_absolute_url")
    instrument_icon = serializers.SlugField(read_only=True, source="instrument.get_icon")
    instrument_unit_of_measure = serializers.CharField(read_only=True, source="instrument.get_unit_of_measure", allow_null=True)
    icon = serializers.CharField(read_only=True, source="get_icon")
    absolute_url = serializers.CharField(read_only=True, source="get_absolute_url")

    class Meta:
        model = AlertItem
        fields = (
            'device_name',
            'device_slug',
            'device_timezone',
            'device_absolute_url',
            'instrument_type',
            'instrument_slug',
            'instrument_absolute_url',
            'instrument_icon',
            'instrument_unit_of_measure',
            'icon',
            'state',
            'absolute_url',
            'datum_timestamp',
            'datum_value',
            'created_at',
        )

    def get_state(self, obj):
        return obj.get_pretty_state()