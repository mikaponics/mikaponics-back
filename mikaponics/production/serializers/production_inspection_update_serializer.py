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

from foundation.models import ProductionInspection
from production.serializers.production_crop_inspection_retrieve_serializer import ProductionCropInspectionRetrieveSerializer


class ProductionInspectionUpdateSerializer(serializers.ModelSerializer):
    state = serializers.IntegerField(required=False)
    did_pass = serializers.BooleanField(required=False)
    failure_reason = serializers.CharField(required=False, allow_blank=True, allow_null=True,)

    class Meta:
        model = ProductionInspection
        fields = (
            'state',
            'did_pass',
            'failure_reason',
            'notes',
        )

    def validate_failure_reason(self, value):
        if self.context['did_pass'] == False:
            if value is None or value == "":
                raise exceptions.ValidationError(_('Please fill in this field.'))
        return value;

    def update(self, instance, validated_data):
        authenticated_by = self.context['authenticated_by']
        authenticated_from = self.context['authenticated_from']
        authenticated_from_is_public = self.context['authenticated_from_is_public']

        state = validated_data.get('state', None)
        if state is not None:
            # STEP 1:
            instance.state = state

            # STEP 2:
            for crop_inspection in instance.crop_inspections.all():
                crop_inspection.state = state
                crop_inspection.last_modified_by = authenticated_by
                crop_inspection.last_modified_from = authenticated_from
                crop_inspection.last_modified_from_is_public = authenticated_from_is_public
                crop_inspection.save()

        # # For debugging purposes only.
        # print("DID PASS:", validated_data.get('did_pass', False))
        # print("FAILURE:", validated_data.get('failure_reason', None))
        # print("NOTES:", validated_data.get('notes', None))

        instance.did_pass = validated_data.get('did_pass', False)
        instance.failure_reason = validated_data.get('failure_reason', None)
        instance.notes = validated_data.get('notes', None)
        instance.last_modified_by = authenticated_by
        instance.last_modified_from = authenticated_from
        instance.last_modified_from_is_public = authenticated_from_is_public
        instance.save()

        return validated_data
