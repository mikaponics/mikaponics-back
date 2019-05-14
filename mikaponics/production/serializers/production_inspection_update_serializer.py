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
        state = validated_data.get('state', None)
        if state is not None:
            instance.state = state

        did_pass = validated_data.get('did_pass', False)

        instance.did_pass = did_pass
        instance.failure_reason = validated_data.get('failure_reason', None)
        instance.notes = validated_data.get('notes', None)
        instance.save()

        return validated_data
