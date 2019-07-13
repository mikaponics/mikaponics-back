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

from foundation.drf import BlankableFloatField, BlankableIntegerField
from foundation.models import CropDataSheet, Production, ProductionCrop
from production.serializers.production_crop_list_serializer import ProductionCropListSerializer


class ProductionCropUpdateSerializer(serializers.ModelSerializer):
    crop_slug = serializers.CharField(required=True, allow_blank=False, source="data_sheet.slug")
    was_harvested = serializers.BooleanField(required=False, allow_null=False,)
    harvest_failure_reason = BlankableIntegerField(required=False, allow_null=True)
    harvest_yield = BlankableIntegerField(required=False, allow_null=True)
    harvest_quality = BlankableIntegerField(required=False, allow_null=True)
    harvest_weight = BlankableFloatField(required=False, allow_null=True)
    average_length = BlankableFloatField(required=False, allow_null=True,)
    average_width = BlankableFloatField(required=False, allow_null=True,)
    average_height = BlankableFloatField(required=False, allow_null=True,)

    class Meta:
        model = ProductionCrop
        fields = (
            'slug',
            'crop_slug',
            'variety',

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
            'average_measure_unit',
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
        # Minor fields.
        instance.variety = validated_data.get('variety', instance.variety)

        # At Finish Fields
        instance.was_harvested = validated_data.get('was_harvested', None)
        instance.harvest_failure_reason = validated_data.get('harvest_failure_reason', None)
        instance.harvest_failure_reason_other = validated_data.get('harvest_failure_reason_other', None)
        instance.harvest_yield = validated_data.get('harvest_yield', None)
        instance.harvest_quality = validated_data.get('harvest_quality', None)
        instance.harvest_notes = validated_data.get('harvest_notes', None)
        instance.harvest_weight = validated_data.get('harvest_weight', None)
        instance.harvest_weight_unit = validated_data.get('harvest_weight_unit', None)
        instance.average_length = validated_data.get('average_length', None)
        instance.average_width = validated_data.get('average_width', None)
        instance.average_height = validated_data.get('average_height', None)
        instance.average_measure_unit = validated_data.get('average_measure_unit', None)
        instance.was_alive_after_harvest = validated_data.get('was_alive_after_harvest', None)
        instance.notes = validated_data.get('notes', None)

        # Audit fields.
        instance.last_modified_by = self.context.get('authenticated_by')
        instance.last_modified_from = self.context.get('authenticated_from')
        instance.last_modified_from_is_public= self.context.get('authenticated_from_is_public')

        # Save and return our data.
        instance.save()
        validated_data['production_crop'] = instance
        return validated_data
