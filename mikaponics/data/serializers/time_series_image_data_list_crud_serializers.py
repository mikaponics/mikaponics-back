# -*- coding: utf-8 -*-
import logging
import pytz
import time
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator

from foundation.models import Device, Instrument, TimeSeriesDatum
# from foundation.model_resources import create_alert_item_in_system_if_possible

logger = logging.getLogger(__name__)


class TimeSeriesImageDataListSerializer(serializers.Serializer):
    instrument_slug = serializers.SlugField(source="instrument.slug")
    value = serializers.FloatField()
    timestamp = serializers.DateTimeField()

    class Meta:
        fields = (
            'instrument_slug',
            'value',
            'timestamp',
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'instrument',
        )
        return queryset
