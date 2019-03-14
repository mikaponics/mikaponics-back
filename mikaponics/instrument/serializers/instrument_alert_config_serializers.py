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


class InstrumentAlertConfigRetrieveUpdateDestroySerializer(serializers.ModelSerializer):

    max_value = serializers.CharField(
        read_only=True,
    )
    red_above_value = serializers.FloatField(
        required=False,
    )
    orange_above_value = serializers.FloatField(
        required=False,
    )
    yellow_above_value = serializers.FloatField(
        required=False,
    )
    yellow_below_value = serializers.FloatField(
        required=False,
    )
    orange_below_value = serializers.FloatField(
        required=False,
    )
    red_below_value = serializers.FloatField(
        required=False,
    )
    red_alert_delay_in_seconds = serializers.IntegerField(
        required=True
    )
    orange_alert_delay_in_seconds = serializers.IntegerField(
        required=True,
    )
    yellow_alert_delay_in_seconds = serializers.IntegerField(
        required=True,
    )
    min_value = serializers.CharField(
        read_only=True,
    )

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
        )
