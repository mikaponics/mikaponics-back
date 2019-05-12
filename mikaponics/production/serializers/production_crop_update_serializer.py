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


class ProductionCropUpdateSerializer(serializers.ModelSerializer):
    # crop = serializers.CharField(required=True, allow_blank=False, source="crop.name")
    crop_slug = serializers.CharField(required=True, allow_blank=False, source="crop.slug")
    # substrate = serializers.CharField(required=True, allow_blank=False, source="substrate.name")
    # substrate_slug = serializers.CharField(required=True, allow_blank=False, source="substrate.slug")
    state_at_finish = serializers.IntegerField(required=True, allow_null=False,)
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
            # 'will_close',
        )

    def validate_state_at_finish(self, value):
        print("validate_state_at_finish | state_at_finish ->", value)
        return value

    def validate_state_failure_reason_at_finish(self, value):
        state_at_finish = self.context['state_at_finish']
        # print("validate_state_failure_reason_at_finish | state_at_finish ->", state_at_finish)
        # print("validate_state_failure_reason_at_finish | failure_reason ->", value)
        if state_at_finish in [ProductionCrop.CROP_STATE_AT_FINISH.CROPS_DIED, ProductionCrop.CROP_STATE_AT_FINISH.CROPS_WERE_TERMINATED]:
            if value == None or value == '' or value == 'None':
                raise exceptions.ValidationError(_('Please fill in this field.'))
        return value

    def validate_harvest_failure_reason_at_finish(self, value):
        harvest_at_finish = self.context['harvest_at_finish']
        # print("validate_state_failure_reason_at_finish | harvest_at_finish ->", harvest_at_finish)
        # print("validate_state_failure_reason_at_finish | failure_reason ->", value)
        if harvest_at_finish in [ProductionCrop.HARVEST_REVIEW.TERRIBLE, ProductionCrop.HARVEST_REVIEW.BAD]:
            if value == None or value == '' or value == 'None':
                raise exceptions.ValidationError(_('Please fill in this field.'))
        return value

    def update(self, instance, validated_data):
        slug = validated_data.get('slug', None)
        crop_slug = validated_data.get('crop_slug', None)
        state_at_finish = validated_data.get('state_at_finish', None)
        state_failure_reason_at_finish = validated_data.get('state_failure_reason_at_finish', None)
        notes_at_finish = validated_data.get('notes_at_finish', None)
        harvest_at_finish = validated_data.get('harvest_at_finish', None)
        harvest_failure_reason_at_finish = validated_data.get('harvest_failure_reason_at_finish', None)
        harvest_notes_at_finish = validated_data.get('harvest_notes_at_finish', None)
        instance.state_at_finish = state_at_finish
        instance.state_failure_reason_at_finish = state_failure_reason_at_finish
        instance.notes_at_finish = notes_at_finish
        instance.harvest_at_finish = harvest_at_finish
        instance.harvest_failure_reason_at_finish = harvest_failure_reason_at_finish
        instance.harvest_notes_at_finish = harvest_notes_at_finish
        instance.save()
        validated_data['production_crop'] = instance
        return validated_data
