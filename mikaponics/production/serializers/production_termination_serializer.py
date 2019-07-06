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

from foundation.models import CropDataSheet, Production
from production.serializers.production_crop_retrieve_serializer import ProductionCropRetrieveSerializer


class ProductionTerminationSerializer(serializers.ModelSerializer):
    finished_at = serializers.DateField(required=True,)
    was_success_at_finish = serializers.BooleanField(required=True,)
    failure_reason = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    notes_at_finish = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    crops = serializers.JSONField(required=True, allow_null=False)

    class Meta:
        model = Production
        fields = (
            'finished_at',
            'was_success_at_finish',
            'failure_reason',
            'notes_at_finish',
            'crops',
        )

    def validate_failure_reason(self, value):
        was_success_at_finish = self.context['was_success_at_finish']
        # print("was_success_at_finish ->", was_success_at_finish)
        # print("failure_reason ->", value)
        if was_success_at_finish == False or was_success_at_finish == 'false' or was_success_at_finish == 'False':
            if value == None or value == '':
                raise exceptions.ValidationError(_('Please fill in this field.'))
        return value

    def update(self, instance, validated_data):
        authenticated_by = self.context.get('authenticated_by')
        authenticated_from = self.context.get('authenticated_from')
        authenticated_from_is_public = self.context.get('authenticated_from_is_public')

        raise exceptions.ValidationError(_('DEVELOPMENT STOP.'))

        # state = validated_data.get('state', None)
        # if state is not None:
        #     # STEP 1:
        #     instance.state = state
        #
        #     # STEP 2:
        #     for crop_inspection in instance.crop_inspections.all():
        #         crop_inspection.state = state
        #         crop_inspection.last_modified_by = authenticated_by
        #         crop_inspection.last_modified_from = authenticated_from
        #         crop_inspection.last_modified_from_is_public = authenticated_from_is_public
        #         crop_inspection.save()
        #
        # # # For debugging purposes only.
        # # print("DID PASS:", validated_data.get('did_pass', False))
        # # print("FAILURE:", validated_data.get('failure_reason', None))
        # # print("NOTES:", validated_data.get('notes', None))
        #
        # instance.did_pass = validated_data.get('did_pass', False)
        # instance.failure_reason = validated_data.get('failure_reason', None)
        # instance.notes = validated_data.get('notes', None)
        # instance.last_modified_by = authenticated_by
        # instance.last_modified_from = authenticated_from
        # instance.last_modified_from_is_public = authenticated_from_is_public
        # instance.save()

        return validated_data
