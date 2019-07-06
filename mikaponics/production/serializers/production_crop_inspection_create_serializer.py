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

from foundation.models import ProductionCrop, ProductionInspection, ProductionCropInspection, CropLifeCycleStage


class ProductionCropInspectionCreateSerializer(serializers.ModelSerializer):
    production_crop = serializers.SlugRelatedField(
        many=False,
        slug_field='slug',
        queryset=ProductionCrop.objects.all(),
        allow_null=False,
        required=True,
    )
    inspection = serializers.SlugRelatedField(
        many=False,
        slug_field='slug',
        queryset=ProductionInspection.objects.all(),
        allow_null=False,
        required=True,
    )
    review = serializers.IntegerField(required=True, allow_null=False,)
    stage = serializers.CharField(required=True, allow_blank=True, allow_null=True,)
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = ProductionCropInspection
        fields = (
            'production_crop',
            'inspection',
            'review',
            'failure_reason',
            'stage',
            'notes',
            'slug',
        )

    def validate_failure_reason(self, value):
        if self.context['review'] in [ProductionCropInspection.REVIEW.TERRIBLE, ProductionCropInspection.REVIEW.BAD,]:
            if value is None or value == "":
                print("ProductionCropInspectionCreateSerializer - validate_failure_reason - failed")
                raise exceptions.ValidationError(_('Please fill in this field.'))
        return value;

    def validate_stage(self, value):
        if CropLifeCycleStage.objects.filter(slug=value).exists() is False:
            raise exceptions.ValidationError(_('Stage does not exist for the stage.'))
        return value

    def create(self, validated_data):
        # Extract our context inputs.
        authenticated_by = self.context['authenticated_by']
        authenticated_from = self.context['authenticated_from']
        authenticated_from_is_public = self.context['authenticated_from_is_public']

        # Extract our inputs.
        production_crop = validated_data.get('production_crop', None)
        inspection = validated_data.get('inspection', None)
        review = validated_data.get('review', None)
        failure_reason = validated_data.get('failure_reason', None)
        stage = validated_data.get('stage', None)
        notes = validated_data.get('notes', None)

        # Extract the stage.
        stage = CropLifeCycleStage.objects.get(slug=stage)

        # Create our object.
        crop_inspection = ProductionCropInspection.objects.create(
            production_crop=production_crop,
            production_inspection=inspection,
            state=ProductionCropInspection.STATE.SUBMITTED,
            review=review,
            failure_reason=failure_reason,
            stage=stage,
            notes=notes,
            created_by=authenticated_by,
            created_from=authenticated_from,
            created_from_is_public=authenticated_from_is_public,
            last_modified_by=authenticated_by,
            last_modified_from=authenticated_from,
            last_modified_from_is_public=authenticated_from_is_public
        )

        # Return our values.
        validated_data['slug'] = crop_inspection.slug
        return validated_data
