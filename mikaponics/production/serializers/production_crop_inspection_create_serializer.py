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

from foundation.models import ProductionCrop, ProductionInspection, ProductionCropInspection, CropLifeCycleStage, ProblemDataSheet
from production.serializers.problem_data_sheet_list_serializer import ProblemDataSheetListSerializer


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
    pest_problems = serializers.JSONField(
        required=False,
        allow_null=True,
    )
    disease_problems = serializers.JSONField(
        required=False,
        allow_null=True,
    )
    abiotic_problems = serializers.JSONField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = ProductionCropInspection
        fields = (
            'production_crop',
            'inspection',
            'review',
            'failure_reason',
            'stage',
            'average_length',
            'average_width',
            'average_height',
            'average_measure_unit',
            'notes',
            'slug',
            'pest_problems',
            'disease_problems',
            'abiotic_problems'
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
        average_length = validated_data.get('average_length', None)
        average_width = validated_data.get('average_width', None)
        average_height = validated_data.get('average_height', None)
        average_measure_unit = validated_data.get('average_measure_unit', None)
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
            average_length=average_length,
            average_width=average_width,
            average_height=average_height,
            average_measure_unit=average_measure_unit,
            notes=notes,
            created_by=authenticated_by,
            created_from=authenticated_from,
            created_from_is_public=authenticated_from_is_public,
            last_modified_by=authenticated_by,
            last_modified_from=authenticated_from,
            last_modified_from_is_public=authenticated_from_is_public
        )

        # Process our `problems`.
        self.process_problems(crop_inspection, validated_data)

        # Return our values.
        validated_data['slug'] = crop_inspection.slug
        return validated_data

    def process_problems(self, crop_inspection, validated_data):
        """
        Function will take the pest, disease and abiotic problems that
        the user inputted and connect these problems to this crop inspection.
        """
        # Get our inputs.
        pest_problems = validated_data.get('pest_problems', [])
        disease_problems = validated_data.get('disease_problems', [])
        abiotic_problems = validated_data.get('abiotic_problems', [])

        # Process inputs.
        for data in pest_problems:
            slug = data.get('slug', None)
            if slug is None: # In case this is from our GUI, this is a convincience code.
                slug = data.get('value', None)
            problem = ProblemDataSheet.objects.filter(slug=slug).first()
            if problem:
                crop_inspection.problems.add(problem)

        for data in disease_problems:
            slug = data.get('slug', None)
            if slug is None: # In case this is from our GUI, this is a convincience code.
                slug = data.get('value', None)
            problem = ProblemDataSheet.objects.filter(slug=slug).first()
            if problem:
                crop_inspection.problems.add(problem)

        for data in abiotic_problems:
            slug = data.get('slug', None)
            if slug is None: # In case this is from our GUI, this is a convincience code.
                slug = data.get('value', None)
            problem = ProblemDataSheet.objects.filter(slug=slug).first()
            if problem:
                crop_inspection.problems.add(problem)
