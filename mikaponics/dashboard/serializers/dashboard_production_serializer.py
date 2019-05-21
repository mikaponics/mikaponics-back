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

from foundation.models import Production, ProductionCrop
from dashboard.serializers.dashboard_production_crop_serializer import DashboardProductionCropListSerializer


logger = logging.getLogger(__name__)


class DashboardProductionListSerializer(serializers.ModelSerializer):
    crops = serializers.SerializerMethodField()
    absolute_url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = Production
        fields = (
            'name',
            'description',
            'crops',
            'evaluation_score',
            'evaluation_has_error',
            'evaluated_at',
            'absolute_url',
        )

    def get_crops(self, obj):
        try:
            crops = obj.crops.all().order_by('-last_modified_at')
            s = DashboardProductionCropListSerializer(crops, many=True)
            return s.data
        except Exception as e:
            print("DashboardProductionListSerializer | get_crops |", e)
            return None
