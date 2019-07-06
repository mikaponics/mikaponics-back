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
from production.serializers.production_crop_retrieve_serializer import ProductionCropRetrieveSerializer
from production.serializers.production_crop_update_serializer import ProductionCropUpdateSerializer


class ProductionTerminationSerializer(serializers.ModelSerializer):
    finished_at = serializers.DateField(required=True,)
    was_success = serializers.BooleanField(required=True,)
    failure_reason = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    notes_at_finish = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    crops = serializers.JSONField(required=True, allow_null=False)

    class Meta:
        model = Production
        fields = (
            'finished_at',
            'was_success',
            'failure_reason',
            'notes_at_finish',
            'crops',
        )

    def validate_failure_reason(self, value):
        was_success = self.context.get('was_success', None)
        if was_success == False or was_success == 'false' or was_success == 'False':
            if value == None or value == '':
                raise exceptions.ValidationError(_('Please fill in this field.'))
        return value

    def update(self, instance, validated_data):
        # Get our inputs
        authenticated_by = self.context.get('authenticated_by')
        authenticated_from = self.context.get('authenticated_from')
        authenticated_from_is_public = self.context.get('authenticated_from_is_public')
        finished_at = validated_data.get('finished_at', None)
        was_success = validated_data.get('was_success', None)
        failure_reason = validated_data.get('failure_reason', None)
        notes_at_finish = validated_data.get('notes_at_finish', None)
        crops = validated_data.get('crops', None)

        # Update the production.
        instance.state = Production.PRODUCTION_STATE.TERMINATED
        instance.finished_at = finished_at
        instance.was_success = was_success
        instance.failure_reason = failure_reason
        instance.notes_at_finish = notes_at_finish
        instance.last_modified_by = authenticated_by
        instance.last_modified_from = authenticated_from
        instance.last_modified_from_is_public = authenticated_from_is_public
        instance.save()

        # Update the production crops.
        self.process_crops(instance, crops)

        return validated_data

    def process_crops(self, production, crops):
        for production_crop_dirty_data in crops:
            # print(production_crop_dirty_data) # For debugging purposes only.
            production_crop_slug = production_crop_dirty_data['production_crop']
            production_crop = ProductionCrop.objects.filter(slug=production_crop_slug).first()
            if production_crop is None:
                raise exceptions.ValidationError(_('Could not find production crop for specified slug.'))

            serializer = ProductionCropUpdateSerializer(production_crop, data=production_crop_dirty_data, context={
                'authenticated_by': self.context.get('authenticated_by'),
                'authenticated_from': self.context.get('authenticated_from'),
                'authenticated_from_is_public': self.context.get('authenticated_from_is_public'),
                'state_at_finish': production_crop_dirty_data.get('state_at_finish'),
                'harvest_at_finish': production_crop_dirty_data.get('harvest_at_finish')
            })
            serializer.is_valid(raise_exception=True)
            serializer.save()
