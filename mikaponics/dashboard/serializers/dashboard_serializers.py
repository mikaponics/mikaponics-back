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

from foundation.models import Device, Invoice, Product, TaskItem, AlertItem
from dashboard.serializers import (
    DashboardDeviceListSerializer,
    DashboardProductionListSerializer
)


logger = logging.getLogger(__name__)


class DashboardSerializer(serializers.Serializer):
    timestamp = serializers.SerializerMethodField()
    devices = serializers.SerializerMethodField()
    productions = DashboardProductionListSerializer(many=True)
    active_alert_items_count = serializers.SerializerMethodField()
    active_task_items_count = serializers.SerializerMethodField()
    # active_alerts_count = serializers.SerializerMethodField()

    # Meta Information.
    class Meta:
        fields = (
            'devices',
            'productions',
        )

    def get_timestamp(self, obj):
        return datetime.now(tz=pytz.utc).timestamp()

    def get_devices(self, obj):
        try:
            user = self.context['authenticated_by']
            active_devices = obj.devices.filter(
                Q(user=user)&
                ~Q(state=Device.DEVICE_STATE.ARCHIVED)
            ).order_by('-last_modified_at')
            s = DashboardDeviceListSerializer(active_devices, many=True)
            serialized_data = s.data
            return serialized_data
        except Exception as e:
            print("DashboardSerializer | get_devices:", e)
            return None

    def get_active_alert_items_count(self, obj):
        try:
            user = self.context['authenticated_by']
            return AlertItem.objects.filter(user=user, state=AlertItem.ALERT_ITEM_STATE.UNREAD).count()
        except Exception as e:
            print("DashboardSerializer | get_active_alert_items_count:", e)
            return None

    def get_active_task_items_count(self, obj):
        try:
            user = self.context['authenticated_by']
            return TaskItem.objects.filter(user=user, is_closed=False).count()
        except Exception as e:
            print("DashboardSerializer | get_active_task_items_count:", e)
            return None
