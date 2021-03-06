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


class ProductionUpdateSerializer(serializers.ModelSerializer):
    day_starts_at = serializers.TimeField(required=False, allow_null=True,)
    day_finishes_at = serializers.TimeField(required=False, allow_null=True,)
    inspection_frequency = serializers.IntegerField(required=True, allow_null=False)

    class Meta:
        model = Production
        fields = (
            'name',
            'description',
            'state',
            'is_commercial',
            'environment',
            'type_of',
            'grow_system',
            'grow_system_other',
            'started_at',
            'finished_at',
            'was_success',
            'failure_reason',
            'notes',
            'has_day_and_night_cycle',
            'day_starts_at',
            'day_finishes_at',
            'inspection_frequency',
            'yellow_below_value',
            'orange_below_value',
            'red_below_value',
            'red_alert_delay_in_seconds',
            'orange_alert_delay_in_seconds',
            'yellow_alert_delay_in_seconds'
        )

    def validate_failure_reason(self, value):
        was_success = self.context['was_success']
        # print("was_success ->", was_success)
        # print("failure_reason ->", value)
        if was_success == False or was_success == 'false' or was_success == 'False':
            if value == None or value == '':
                raise exceptions.ValidationError(_('Please fill in this field.'))
        return value
