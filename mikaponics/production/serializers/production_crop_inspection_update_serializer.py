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

from foundation.models import ProductionCropInspection


class ProductionCropInspectionUpdateSerializer(serializers.ModelSerializer):
    review = serializers.IntegerField(required=True)
    stage = serializers.IntegerField(required=True)

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

    def update(self, instance, validated_data):
        authenticated_by = self.context['authenticated_by']
        authenticated_from = self.context['authenticated_from']
        authenticated_from_is_public = self.context['authenticated_from_is_public']

        state = validated_data.get('state', None)
        if state is not None:
            instance.state = state

        review = validated_data.get('review', None)
        stage = validated_data.get('stage', None)

        instance.review = review
        instance.failure_reason = validated_data.get('failure_reason', None)
        instance.stage = validated_data.get('stage', None)
        instance.notes = validated_data.get('notes', None)
        instance.last_modified_by = authenticated_by
        instance.last_modified_from = authenticated_from
        instance.last_modified_from_is_public = authenticated_from_is_public
        instance.save()

        return validated_data