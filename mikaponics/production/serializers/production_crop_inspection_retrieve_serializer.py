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

from foundation.models import ProductionCropInspection


class ProductionCropInspectionRetrieveSerializer(serializers.ModelSerializer):
    pretty_state = serializers.ReadOnlyField(source="get_pretty_state")
    pretty_review = serializers.ReadOnlyField(source="get_pretty_review")
    pretty_stage = serializers.ReadOnlyField(source="get_pretty_stage")
    production_crop_name = serializers.CharField(required=True, allow_blank=False, source="production_crop.get_pretty_name")
    production_crop_quantity = serializers.IntegerField(required=True, source="production_crop.quantity")
    production_crop_substrate = serializers.CharField(required=True, allow_blank=False, source="production_crop.get_pretty_substrate_name")
    production_crop_stages = serializers.ReadOnlyField(source="production_crop.data_sheet.stages_dict")
    production_crop_slug = serializers.SlugField(required=True, allow_blank=False, source="production_crop.slug")
    production_crop_absolute_url = serializers.CharField(required=True, allow_blank=False, source="production_crop.get_absolute_url")
    # absolute_url = serializers.CharField(required=True, allow_blank=False, source="get_absolute_url") #TODO: IMPL.
    stage = serializers.IntegerField(required=True, allow_null=True)

    class Meta:
        model = ProductionCropInspection
        fields = (
            'production_crop_name',
            'production_crop_quantity',
            'production_crop_substrate',
            'production_crop_stages',
            'production_crop_slug',
            'production_crop_absolute_url',
            'state',
            'pretty_state',
            'pretty_review',
            'pretty_stage',
            'slug',
            # 'absolute_url', #TODO: IMPL.
            'review',
            'failure_reason',
            'stage',
            'notes',
            'created_at',
            'last_modified_at'
        )
