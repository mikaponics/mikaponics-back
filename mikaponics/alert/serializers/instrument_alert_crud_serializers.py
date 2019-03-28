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

from foundation.models import InstrumentAlert


class InstrumentAlertListSerializer(serializers.ModelSerializer):

    state = serializers.SerializerMethodField()
    device_name = serializers.CharField(read_only=True, source="instrument.device.name")
    device_slug = serializers.SlugField(read_only=True, source="instrument.device.slug")
    device_absolute_url = serializers.SlugField(read_only=True, source="instrument.device.get_absolute_url")
    instrument_type = serializers.CharField(read_only=True, source="instrument.get_pretty_instrument_type_of")
    instrument_slug = serializers.SlugField(read_only=True, source="instrument.slug")
    instrument_absolute_url = serializers.SlugField(read_only=True, source="instrument.get_absolute_url")

    class Meta:
        model = InstrumentAlert
        fields = (
            'device_name',
            'device_slug',
            'device_absolute_url',
            'instrument_type',
            'instrument_slug',
            'instrument_absolute_url',
            'datum_timestamp',
            'datum_value',
            'state',
            'created_at',
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
#
#
# class InstrumentRetrieveUpdateSerializer(serializers.ModelSerializer):
#
#     absolute_parent_url = serializers.SerializerMethodField()
#     absolute_url = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Instrument
#         fields = (
#             'max_value',
#             'red_above_value',
#             'orange_above_value',
#             'yellow_above_value',
#             'yellow_below_value',
#             'orange_below_value',
#             'red_below_value',
#             'red_alert_delay_in_seconds',
#             'orange_alert_delay_in_seconds',
#             'yellow_alert_delay_in_seconds',
#             'min_value',
#             'absolute_parent_url',
#             'absolute_url',
#             'slug',
#         )
#
#     def get_absolute_parent_url(self, obj):
#         return obj.device.get_absolute_url()
#
#     def get_absolute_url(self, obj):
#         return obj.get_absolute_url()
