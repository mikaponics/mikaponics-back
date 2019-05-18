# -*- coding: utf-8 -*-
import logging
import pytz
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db.models import Q, Prefetch, Sum
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator

from foundation.models import Device, Invoice, Product


logger = logging.getLogger(__name__)


class DashboardDeviceListSerializer(serializers.ModelSerializer):
    absolute_url = serializers.ReadOnlyField(source='get_absolute_url')
    state = serializers.ReadOnlyField(source='get_pretty_state')
    last_measured_pretty_value = serializers.ReadOnlyField(source='get_pretty_last_measured_value')
    last_measured_pretty_at = serializers.ReadOnlyField(source='get_pretty_last_measured_at')

    class Meta:
        model = Device
        fields = (
            'name',
            'description',
            'state',
            'last_measured_value',
            'last_measured_pretty_value',
            'last_measured_pretty_at',
            'last_measured_at',
            'last_measured_unit_of_measure',
            'absolute_url',
        )
