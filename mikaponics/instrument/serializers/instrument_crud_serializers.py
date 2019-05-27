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

from foundation.models import Instrument


class InstrumentListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Instrument
        fields = (
            'slug',
            'absolute_url',
        )


class InstrumentRetrieveUpdateSerializer(serializers.ModelSerializer):

    absolute_parent_url = serializers.SerializerMethodField()
    absolute_url = serializers.SerializerMethodField()
    icon = serializers.CharField(read_only=True, source='get_icon')
    unit_of_measure = serializers.CharField(read_only=True, source='get_unit_of_measure')
    timezone = serializers.ReadOnlyField(source='device.timezone')
    pretty_type_of = serializers.CharField(read_only=True, source='get_pretty_instrument_type_of')
    last_camera_snapshot = serializers.ImageField(source="last_camera_snapshot.image_value", read_only=True)

    class Meta:
        model = Instrument
        fields = (
            'max_value',
            'red_above_value',
            'orange_above_value',
            'yellow_above_value',
            'yellow_below_value',
            'orange_below_value',
            'red_below_value',
            'red_alert_delay_in_seconds',
            'orange_alert_delay_in_seconds',
            'yellow_alert_delay_in_seconds',
            'min_value',
            'absolute_parent_url',
            'absolute_url',
            'slug',
            'icon',
            'state',
            'last_camera_snapshot',
            'last_measured_value',
            'last_measured_at',
            'last_24h_min_value',
            'last_24h_min_timestamp_at',
            'last_24h_max_value',
            'last_24h_max_timestamp_at',
            'last_24h_mean_value',
            'last_24h_median_value',
            'last_24h_mode_value',
            'last_24h_mode_values',
            'last_24h_range_value',
            'last_24h_stedv_value',
            'last_24h_variance_value',
            'unit_of_measure',
            'type_of',
            'pretty_type_of',
            'timezone',
        )

    def get_absolute_parent_url(self, obj):
        return obj.device.get_absolute_url()

    def get_absolute_url(self, obj):
        return obj.get_absolute_url()
