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

from foundation.models import ProductionCrop


logger = logging.getLogger(__name__)


class DashboardProductionCropListSerializer(serializers.ModelSerializer):
    pretty_name = serializers.ReadOnlyField(source="get_pretty_name")
    pretty_score = serializers.ReadOnlyField(source="get_evaluation_letter")
    absolute_url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = ProductionCrop
        fields = (
            'pretty_name',
            'pretty_score',
            'evaluation_score',
            'evaluation_error',
            'evaluated_at',
            'absolute_url',
        )
