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

from foundation.models import Crop, Production, ProductionCrop
from production.serializers.production_crop_list_serializer import ProductionCropListSerializer


class ProductionCropTerminationSerializer(serializers.ModelSerializer):
    # crop = serializers.CharField(required=True, allow_blank=False, source="crop.name")
    crop_slug = serializers.CharField(required=True, allow_blank=False, source="crop.slug")
    # substrate = serializers.CharField(required=True, allow_blank=False, source="substrate.name")
    # substrate_slug = serializers.CharField(required=True, allow_blank=False, source="substrate.slug")
    state_at_finish = serializers.IntegerField(required=True,)
    state_failure_reason_at_finish = serializers.CharField(required=False, allow_blank=True, allow_null=True,)
    notes_at_finish = serializers.CharField(required=False, allow_blank=True, allow_null=True,)
    harvest_at_finish = serializers.IntegerField(required=True,)
    harvest_failure_reason_at_finish = serializers.CharField(required=False, allow_blank=True, allow_null=True,)
    harvest_notes_at_finish = serializers.CharField(required=False, allow_blank=True, allow_null=True,)

    class Meta:
        model = ProductionCrop
        fields = (
            'slug',
            'crop_slug',
            'state_at_finish',
            'state_failure_reason_at_finish',
            'notes_at_finish',
            'harvest_at_finish',
            'harvest_failure_reason_at_finish',
            'harvest_notes_at_finish',
        )

    def create(self, validated_data):
        print("------------------")
        slug = validated_data.get('slug', None)
        crop_slug = validated_data.get('crop_slug', None)
        state_at_finish = validated_data.get('state_at_finish', None)
        state_failure_reason_at_finish = validated_data.get('state_failure_reason_at_finish', None)
        notes_at_finish = validated_data.get('notes_at_finish', None)
        harvest_at_finish = validated_data.get('harvest_at_finish', None)
        harvest_failure_reason_at_finish = validated_data.get('harvest_failure_reason_at_finish', None)
        harvest_notes_at_finish = validated_data.get('harvest_notes_at_finish', None)
        print(
            slug,
            crop_slug,
            state_at_finish,
            state_failure_reason_at_finish,
            notes_at_finish,
            harvest_at_finish,
            harvest_failure_reason_at_finish,
            harvest_notes_at_finish,
        )
        return validated_data

class ProductionTerminationSerializer(serializers.ModelSerializer):

    plants = serializers.JSONField(required=True, allow_null=True,)
    fish = serializers.JSONField(required=True, allow_null=True,)

    class Meta:
        model = Production
        fields = (
            'plants',
            'fish',
        )

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        # Get our context data.
        authenticated_user = self.context['authenticated_by']
        authenticated_user_from = self.context['authenticated_from']
        authenticated_user_from_is_public = self.context['authenticated_from_is_public']

        # Get our inputted data.
        plants = validated_data.get('plants', None)
        fish = validated_data.get('fish', None)

        # Iterate through all the entries and save them.
        plants_serializer = ProductionCropTerminationSerializer(data=plants, context={
            'authenticated_by': authenticated_user,
            'authenticated_from': authenticated_user_from,
            'authenticated_from_is_public': authenticated_user_from_is_public,
        }, many=True)
        plants_serializer.is_valid(raise_exception=True)
        plants_serializer.save()

        #TODO: IMPLEMENT...

        # instance.invoice.invalidate('total')
        return validated_data
