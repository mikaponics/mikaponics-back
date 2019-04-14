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
        )

    def get_absolute_parent_url(self, obj):
        return obj.device.get_absolute_url()

    def get_absolute_url(self, obj):
        return obj.get_absolute_url()
