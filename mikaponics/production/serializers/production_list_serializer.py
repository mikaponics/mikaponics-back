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

from foundation.models import Production


class ProductionListSerializer(serializers.ModelSerializer):
    pretty_state = serializers.CharField(required=True, allow_blank=False, source="get_pretty_state")
    pretty_environment = serializers.CharField(required=True, allow_blank=False, source="get_pretty_environment")
    pretty_type_of = serializers.CharField(required=True, allow_blank=False, source="get_pretty_type_of")
    # pretty_system serializers.CharField(required=True, allow_blank=False, source="get_pretty_system")

    class Meta:
        model = Production
        fields = (
            'state',
            'pretty_state',
            'slug',
            'is_commercial',
            'environment',
            'pretty_environment',
            'type_of',
            'pretty_type_of',
            'system',
            # 'pretty_system',
            'system_other',
            'started_at',
            'finished_at',
        )
