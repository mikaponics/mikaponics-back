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

from foundation.models import ProductionCropInspection, CropLifeCycleStage


class ProductionCropInspectionUpdateSerializer(serializers.ModelSerializer):
    review = serializers.IntegerField(required=True)
    stage = serializers.CharField(required=True, allow_blank=True, allow_null=True,)

    class Meta:
        model = ProductionCropInspection
        fields = (
            'review',
            'failure_reason',
            'stage',
            'notes',
        )

    def validate_failure_reason(self, value):
        if self.context['review'] in [ProductionCropInspection.REVIEW.TERRIBLE, ProductionCropInspection.REVIEW.BAD,]:
            if value is None or value == "":
                raise exceptions.ValidationError(_('Please fill in this field.'))
        return value;

    def validate_stage(self, value):
        if CropLifeCycleStage.objects.filter(slug=value).exists() is False:
            raise exceptions.ValidationError(_('Stage does not exist for the stage.'))
        return value

    def update(self, instance, validated_data):
        # Extract our context inputs.
        authenticated_by = self.context['authenticated_by']
        authenticated_from = self.context['authenticated_from']
        authenticated_from_is_public = self.context['authenticated_from_is_public']

        # Extract our inputs.
        state = validated_data.get('state', ProductionCropInspection.STATE.DRAFT)
        if state is not None:
            instance.state = state
        review = validated_data.get('review', None)
        notes = validated_data.get('notes', None)

        # # For debugging purposes only.
        # print("SLUG:", instance.slug)
        # print("STATE:", state)
        # print("REVIEW:", review)
        # print("NOTES:", notes)

        # Extract the stage.
        stage = validated_data.get('stage', None)
        stage = CropLifeCycleStage.objects.get(slug=stage)

        instance.review = review
        instance.failure_reason = validated_data.get('failure_reason', None)
        instance.stage = stage
        instance.notes = notes
        instance.last_modified_by = authenticated_by
        instance.last_modified_from = authenticated_from
        instance.last_modified_from_is_public = authenticated_from_is_public
        instance.save()
        return validated_data
