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

from foundation.models import CropDataSheet, Production, ProductionCrop
from production.serializers.production_crop_list_serializer import ProductionCropListSerializer


class ProductionCropUpdateSerializer(serializers.ModelSerializer):
    crop_slug = serializers.CharField(required=True, allow_blank=False, source="data_sheet.slug")
    was_harvested = serializers.BooleanField(required=False, allow_null=False,)
    harvest_failure_reason = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    harvest_yield = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    harvest_quality = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    harvest_weight = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = ProductionCrop
        fields = (
            'slug',
            'crop_slug',

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
        )

    def validate_harvest_failure_reason(self, value):
        was_harvested = self.context.get('was_harvested', None)
        if was_harvested == False or was_harvested == 'false':
            if value == None or value == '' or value == 'None':
                raise exceptions.ValidationError(_('Please fill in this field.'))
        return value

    def validate_harvest_failure_reason_other(self, value):
        harvest_failure_reason = self.context.get('harvest_failure_reason', None)
        if harvest_failure_reason == ProductionCrop.HARVEST_FAILURE_REASON.OTHER_PROBLEM:
            if value == None or value == '' or value == 'None':
                raise exceptions.ValidationError(_('Please fill in this field.'))
        return value

    def validate_harvest_yield(self, value):
        was_harvested = self.context.get('was_harvested', None)
        if was_harvested == True or was_harvested == 'true':
            if value == None or value == '' or value == 'None':
                raise exceptions.ValidationError(_('Please fill in this field.'))
        return value

    def validate_harvest_quality(self, value):
        was_harvested = self.context.get('was_harvested', None)
        if was_harvested == True or was_harvested == 'true':
            if value == None or value == '' or value == 'None':
                raise exceptions.ValidationError(_('Please fill in this field.'))
        return value

    def update(self, instance, validated_data):
        slug = validated_data.get('slug', None)
        crop_slug = validated_data.get('crop_slug', None)
        state_at_finish = validated_data.get('state_at_finish', None)
        state_failure_reason_at_finish = validated_data.get('state_failure_reason_at_finish', None)
        notes = validated_data.get('notes', None)
        harvest_at_finish = validated_data.get('harvest_at_finish', None)
        harvest_failure_reason_at_finish = validated_data.get('harvest_failure_reason_at_finish', None)
        harvest_notes = validated_data.get('harvest_notes', None)
        instance.state_at_finish = state_at_finish
        instance.state_failure_reason_at_finish = state_failure_reason_at_finish
        instance.notes = notes
        instance.harvest_at_finish = harvest_at_finish
        instance.harvest_failure_reason_at_finish = harvest_failure_reason_at_finish
        instance.harvest_notes = harvest_notes
        instance.last_modified_by = self.context.get('authenticated_by')
        instance.last_modified_from = self.context.get('authenticated_from')
        instance.last_modified_from_is_public= self.context.get('authenticated_from_is_public')
        instance.save()
        validated_data['production_crop'] = instance
        return validated_data
