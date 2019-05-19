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

from foundation.models import Production, ProductionCrop
from production.serializers.production_crop_retrieve_serializer import ProductionCropRetrieveSerializer
from device.serializers.device_crud_api_serializers import DeviceRetrieveUpdateDestroySerializer


class ProductionRetrieveSerializer(serializers.ModelSerializer):
    pretty_state = serializers.CharField(required=True, allow_blank=False, source="get_pretty_state")
    pretty_environment = serializers.CharField(required=True, allow_blank=False, source="get_pretty_environment")
    pretty_type_of = serializers.CharField(required=True, allow_blank=False, source="get_pretty_type_of")
    pretty_grow_system = serializers.CharField(required=True, allow_blank=False, source="get_pretty_grow_system")
    absolute_url = serializers.CharField(required=True, allow_blank=False, source="get_absolute_url")
    plants = serializers.SerializerMethodField()
    fish = serializers.SerializerMethodField()
    crops = serializers.SerializerMethodField()
    device = DeviceRetrieveUpdateDestroySerializer(many=False, required=True)

    class Meta:
        model = Production
        fields = (
            'name',
            'description',
            'state',
            'pretty_state',
            'slug',
            'is_commercial',
            'environment',
            'pretty_environment',
            'type_of',
            'pretty_type_of',
            'grow_system',
            'pretty_grow_system',
            'grow_system_other',
            'started_at',
            'finished_at',
            'was_success_at_finish',
            'failure_reason',
            'notes_at_finish',
            'plants',
            'fish',
            'crops',
            'device',
            'absolute_url',
        )

    def get_plants(self, obj):
        try:
            plants = obj.crops.filter(
                type_of=ProductionCrop.TYPE_OF.PLANT
            ).order_by('id')
            s = ProductionCropRetrieveSerializer(plants, many=True)
            return s.data;
        except Exception as e:
            print("ProductionRetrieveSerializer | get_plants |", e)
            return []

    def get_fish(self, obj):
        try:
            fish = obj.crops.filter(
                type_of=ProductionCrop.TYPE_OF.FISHSTOCK
            ).order_by('id')
            s = ProductionCropRetrieveSerializer(fish, many=True)
            return s.data;
        except Exception as e:
            print("ProductionRetrieveSerializer | get_fish |", e)
            return []

    def get_crops(self, obj):
        try:
            crops = obj.crops.order_by('id')
            s = ProductionCropRetrieveSerializer(crops, many=True)
            return s.data;
        except Exception as e:
            print("ProductionRetrieveSerializer | get_crops |", e)
            return []
