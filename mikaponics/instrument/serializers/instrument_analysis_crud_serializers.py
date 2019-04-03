# -*- coding: utf-8 -*-
import pytz
from datetime import datetime, timedelta
from dateutil import tz
from dateutil.parser import *
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
from instrument.model_resources import generate_instrument_analysis


class InstrumentAnalysisListCreateSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(read_only=True)
    instrument_slug = serializers.SlugField(read_only=True, source="instrument.slug")
    instrument_slug = serializers.SlugField(write_only=True)
    timezone_name = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    instrument_absolute_url = serializers.SlugField(read_only=True, source="instrument.get_absolute_url")
    absolute_url = serializers.ReadOnlyField(source="get_absolute_url")
    start_dt = serializers.DateTimeField(
        required=True,
        input_formats=['iso-8601']
    )
    finish_dt = serializers.DateTimeField(
        required=True,
        input_formats=['iso-8601']
    )

    class Meta:
        model = InstrumentAnalysis
        fields = (
            'absolute_url',
            'slug',
            'instrument_slug',
            'instrument_absolute_url',
            'start_dt',
            'finish_dt',
            'timezone_name',
            # 'min_value',
            # 'min_timestamp',
            # 'max_value',
            # 'max_timestamp',
            # 'mean_value',
            # 'median_value',
            # 'mode_value',
            # 'mode_values',
            # 'range_value',
            # 'stedv_value',
            # 'variance_value',
            'created_at',
            'last_modified_at'
        )

    def create(self, validated_data):
        # Fetch our outputs.
        naive_start_dt = validated_data.get('start_dt')
        naive_finish_dt = validated_data.get('finish_dt')
        instrument_slug = validated_data.get('instrument_slug')
        timezone_name = validated_data.get('timezone_name', "UTC")

        # Convert our datetimes to be timezone specific.
        local_timezone = pytz.timezone(timezone_name)
        aware_start_dt = naive_start_dt.replace(tzinfo=local_timezone)
        aware_finish_dt = naive_finish_dt.replace(tzinfo=local_timezone)

        # Generate our analysis.
        try:
            analysis = generate_instrument_analysis(
                instrument_slug=instrument_slug,
                aware_start_dt=aware_start_dt,
                aware_finish_dt=aware_finish_dt
            )
        except Exception as e:
            raise exceptions.ValidationError({
                'non_field_errors': [
                    str(e),
                ]
            })

        # Return our created object.
        return analysis


class InstrumentAnalysisRetrieveUpdateSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(read_only=True)
    instrument_slug = serializers.SlugField(read_only=True, source="instrument.slug")
    instrument_absolute_url = serializers.SlugField(read_only=True, source="instrument.get_absolute_url")
    absolute_url = serializers.ReadOnlyField(source="get_absolute_url")

    class Meta:
        model = InstrumentAnalysis
        fields = (
            'absolute_url',
            'slug',
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
