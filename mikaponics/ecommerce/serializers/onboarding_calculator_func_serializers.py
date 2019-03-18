# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Q, Prefetch, Sum
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator

from ecommerce.models.product import Product


logger = logging.getLogger(__name__)


class OnboardingCalculatorFuncSerializer(serializers.Serializer):
    number_of_devices = serializers.IntegerField(required=True)
    shipping_address_country = serializers.CharField(required=True,allow_blank=False,)
    shipping_address_region = serializers.CharField(required=True,allow_blank=False,)
    calculation = serializers.JSONField(read_only=True)

    # Meta Information.
    class Meta:
        fields = (
            'number_of_devices',
            'shipping_address_country',
            'shipping_address_region',
            'calculation',
        )

    @transaction.atomic
    def create(self, validated_data):
        validated_data['calculation'] = {
            'monthlyFee': 111,
            'numberOfDevices': 1,
            'pricePerDevice': 222,
            'totalBeforeTax': 333,
            'tax': 444,
            'totalAfterTax': 555,
            'shipping': 6,
            'credit': 7,
            'grandTotal': 8,
        };
        return validated_data
