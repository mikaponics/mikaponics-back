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

from foundation.models import ProductionInspection
from production.serializers.production_crop_inspection_retrieve_serializer import ProductionCropInspectionRetrieveSerializer


class ProductionInspectionRetrieveSerializer(serializers.ModelSerializer):
    pretty_state = serializers.ReadOnlyField(source="get_pretty_state")
    production_slug = serializers.SlugField(required=True, allow_blank=False, source="production.slug")
    production_absolute_url = serializers.CharField(required=True, allow_blank=False, source="production.get_absolute_url")
    absolute_url = serializers.CharField(required=True, allow_blank=False, source="get_absolute_url")
    crops = serializers.SerializerMethodField()

    class Meta:
        model = ProductionInspection
        fields = (
            'production_slug',
            'production_absolute_url',
            'state',
            'pretty_state',
            'slug',
            'absolute_url',
            'did_pass',
            'failure_reason',
            'notes',
            'created_at',
            'last_modified_at',
            'crops',
        )

    def get_crops(self, obj):
        try:
            crops = obj.crop_inspections.order_by('id')
            s = ProductionCropInspectionRetrieveSerializer(crops, many=True)
            return s.data;
        except Exception as e:
            print("ProductionInspectionRetrieveSerializer | get_crops |", e)
            return []
