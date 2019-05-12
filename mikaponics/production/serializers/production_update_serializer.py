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

from foundation.models import Crop, Production
from production.serializers.production_crop_retrieve_serializer import ProductionCropRetrieveSerializer


class ProductionUpdateSerializer(serializers.ModelSerializer):
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
            'failure_reason_at_finish',
            'notes_at_finish',
        )

    def validate_failure_reason_at_finish(self, value):
        was_success_at_finish = self.context['was_success_at_finish']
        print("was_success_at_finish", was_success_at_finish)
        print("failure_reason_at_finish", value)
        if was_success_at_finish == False or value == 'false' or value == 'False':
            if value == None or value == '':
                raise exceptions.ValidationError(_('Please fill in this field.'))
        return value
