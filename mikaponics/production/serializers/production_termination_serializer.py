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

from foundation.models import Crop, Production
from production.serializers.production_crop_list_serializer import ProductionCropListSerializer


class ProductionTerminationRetrieveSerializer(serializers.ModelSerializer):
    absoluteURL = serializers.CharField(required=True, allow_blank=False, source="get_absolute_url")
    plants = serializers.SerializerMethodField()
    fish = serializers.SerializerMethodField()

    class Meta:
        model = Production
        fields = (
            'state',
            'pretty_state',
            'slug',
            'plants',
            'fish',
            'absoluteURL',
        )

    def get_plants(self, obj):
        try:
            plants = obj.crops.filter(crop__type_of=Crop.TYPE_OF.PLANT)
            s = ProductionCropListSerializer(plants, many=True)
            return s.data;
        except Exception as e:
            print("ProductionRetrieveSerializer | get_plants |", e)
            return []

    def get_fish(self, obj):
        try:
            fish = obj.crops.filter(crop__type_of=Crop.TYPE_OF.FISHSTOCK)
            s = ProductionCropListSerializer(fish, many=True)
            return s.data;
        except Exception as e:
            print("ProductionRetrieveSerializer | get_fish |", e)
            return []
