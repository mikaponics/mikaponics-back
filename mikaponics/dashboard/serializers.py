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

from foundation.models import Invoice, Product


logger = logging.getLogger(__name__)


class DashboardSerializer(serializers.Serializer):
    timestamp = serializers.SerializerMethodField()
    devices = serializers.SerializerMethodField()

    # Meta Information.
    class Meta:
        fields = (
            'devices',
        )

    def get_timestamp(self, obj):
        return datetime.now(tz=pytz.utc).timestamp()

    def get_devices(self, obj):
        user = self.context['authenticated_by']
        arr = []
        for device in user.devices.all():
            arr.append({
                'name': "Your device" if device.name is '' else device.name,
                'description': "Your device description goes here..." if device.description is '' else device.description,
                'state': device.get_pretty_state(),
                'last_measured_timestamp': device.pretty_last_measured_timestamp,
                'absolute_url': device.get_absolute_url(),
            })
        return arr
