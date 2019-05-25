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
            'was_success_at_finish',
            'failure_reason',
            'notes_at_finish',
            'has_day_and_night_cycle',
            'day_starts_at',
            'day_finishes_at',
            'inspection_frequency',
            #TODO: ALERT RED/ORANGE/YELLOW
        )

    def validate_failure_reason(self, value):
        was_success_at_finish = self.context['was_success_at_finish']
        # print("was_success_at_finish ->", was_success_at_finish)
        # print("failure_reason ->", value)
        if was_success_at_finish == False or was_success_at_finish == 'false' or was_success_at_finish == 'False':
            if value == None or value == '':
                raise exceptions.ValidationError(_('Please fill in this field.'))
        return value
