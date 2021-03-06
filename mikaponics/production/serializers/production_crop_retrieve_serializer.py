# -*- coding: utf-8 -*-
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string  # HTML / TXT
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework.response import Response

from foundation.models import ProductionCrop


class ProductionCropRetrieveSerializer(serializers.ModelSerializer):
    pretty_name = serializers.ReadOnlyField(source="get_pretty_name")
    evaluation_letter = serializers.ReadOnlyField(source="get_evaluation_letter")
    # pretty_state_at_finish = serializers.ReadOnlyField(source="get_pretty_state_at_finish")
    data_sheet = serializers.CharField(required=True, allow_blank=False, source="data_sheet.name")
    crop_slug = serializers.CharField(required=True, allow_blank=False, source="data_sheet.slug")
    substrate = serializers.CharField(required=True, allow_blank=False, source="substrate.name")
    substrate_slug = serializers.CharField(required=True, allow_blank=False, source="substrate.slug")
    absolute_url = serializers.CharField(required=True, allow_blank=False, source="get_absolute_url")

    class Meta:
        model = ProductionCrop
        fields = (
            'pretty_name',
            # 'pretty_state_at_finish',
            'data_sheet',
            'data_sheet_other',
            'variety',
            'crop_slug',
            'quantity',
            'substrate',
            'substrate_other',
            'substrate_slug',
            'stage',

            # At Finish Fields
            'was_harvested',
            'harvest_failure_reason',
            'harvest_failure_reason_other',
            'harvest_yield',
            'harvest_quality',
            'harvest_notes',
            'harvest_weight',
            'harvest_weight_unit',
            'average_length',
            'average_width',
            'average_height',
            'was_alive_after_harvest',
            'notes',

            'created_at',
            'last_modified_at',
            'slug',
            'type_of',
            'evaluation_score',
            'evaluation_letter',
            'evaluation_error',
            'evaluation_passes',
            'evaluation_failures',
            'evaluated_at',
            'absolute_url',
        )
