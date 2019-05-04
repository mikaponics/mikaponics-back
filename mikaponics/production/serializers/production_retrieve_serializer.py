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


class ProductionRetrieveSerializer(serializers.ModelSerializer):
    # state = serializers.CharField(required=True, allow_blank=False)
    # password_repeat = serializers.CharField(required=True, allow_blank=False)
    # first_name = serializers.CharField(required=True, allow_blank=False)
    # last_name = serializers.CharField(required=True, allow_blank=False)
    # timezone = serializers.CharField(required=True, allow_blank=False)
    # has_signed_tos = serializers.BooleanField(required=True)
    # referral_code = serializers.CharField(required=False, allow_blank=True, allow_null=True,)

    class Meta:
        model = Production
        fields = (
            'state',
            # 'red_above_value',
            # 'orange_above_value',
            # 'yellow_above_value',
            # 'yellow_below_value',
            # 'orange_below_value',
            # 'red_below_value',
            # 'red_alert_delay_in_seconds',
            # 'orange_alert_delay_in_seconds',
            # 'yellow_alert_delay_in_seconds',
            # 'min_value',
        )
