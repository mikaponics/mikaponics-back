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

from foundation.models import InstrumentAnalysis


class InstrumentAnalysisListCreateSerializer(serializers.ModelSerializer):

    instrument_slug = serializers.SlugField(read_only=True, source="instrument.slug")
    instrument_absolute_url = serializers.SlugField(read_only=True, source="instrument.get_absolute_url")

    class Meta:
        model = InstrumentAnalysis
        fields = (
            'instrument_slug',
            'instrument_absolute_url',
            'start_dt',
            'finish_dt',
            'min_value',
            'min_timestamp',
            'max_value',
            'max_timestamp',
            'mean_value',
            'median_value',
            'mode_value',
            'mode_values',
            'range_value',
            'stedv_value',
            'variance_value',
            'created_at',
            'last_modified_at'
        )

    def create(self, validated_data):

        # Return our calculations.
        return validated_data
