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


logger = logging.getLogger(__name__)


def get_todays_date_plus_days(days=0):
    """Returns the current date plus paramter number of days."""
    return timezone.now() + timedelta(days=days)


class OnboardingSubmissionFuncSerializer(serializers.Serializer):
    # Purchase.
    number_of_devices = serializers.IntegerField(required=True)
    stripe_token = serializers.CharField(required=True,allow_blank=False,)

    # Billing address.
    billing_given_name = serializers.CharField(required=True,allow_blank=False,)
    billing_last_name = serializers.CharField(required=True,allow_blank=False,)
    billing_address_country = serializers.CharField(required=True,allow_blank=False,)
    billing_address_region = serializers.CharField(required=True,allow_blank=False,)
    billing_address_locality = serializers.CharField(required=True,allow_blank=False,)
    billing_postal_code = serializers.CharField(required=True,allow_blank=False,)
    billing_street_address = serializers.CharField(required=True,allow_blank=False,)
    billing_postal_code = serializers.CharField(required=True,allow_blank=False,)
    billing_post_office_box_number = serializers.CharField(required=False,allow_blank=True,)
    billing_email = serializers.CharField(required=True,allow_blank=False,)
    billing_telephone = serializers.CharField(required=True,allow_blank=False,)

    # Shipping address.
    shipping_given_name = serializers.CharField(required=True,allow_blank=False,)
    shipping_last_name = serializers.CharField(required=True,allow_blank=False,)
    shipping_address_country = serializers.CharField(required=True,allow_blank=False,)
    shipping_address_region = serializers.CharField(required=True,allow_blank=False,)
    shipping_address_locality = serializers.CharField(required=True,allow_blank=False,)
    shipping_postal_code = serializers.CharField(required=True,allow_blank=False,)
    shipping_street_address = serializers.CharField(required=True,allow_blank=False,)
    shipping_postal_code = serializers.CharField(required=True,allow_blank=False,)
    shipping_post_office_box_number = serializers.CharField(required=False,allow_blank=True,)
    shipping_email = serializers.CharField(required=True,allow_blank=False,)
    shipping_telephone = serializers.CharField(required=True,allow_blank=False,)

    # Meta Information.
    class Meta:
        fields = (
            # Purchase.
            'number_of_devices',
            'stripe_token',

            # Billing address.
            'billing_given_name',
            'billing_last_name',
            'billing_address_country',
            'billing_address_region',
            'billing_address_locality',
            'billing_postal_code',
            'billing_street_address',
            'billing_postal_code',
            'billing_post_office_box_number',
            'billing_email',
            'billing_telephone',

            # Shipping address.
            'shipping_given_name',
            'shipping_last_name',
            'shipping_address_country',
            'shipping_address_region',
            'shipping_address_locality',
            'shipping_postal_code',
            'shipping_street_address',
            'shipping_postal_code',
            'shipping_post_office_box_number',
            'shipping_email',
            'shipping_telephone',
        )

    def validate_number_of_devices(self, data):
        number_of_devices = data
        if number_of_devices > 50:
            raise exceptions.ValidationError({
                'number_of_devices': _('Cannot order more then 50 devices in one order, please contact <a href="mailto:info@mikaponics.com">info@mikasoftware.com</a> to order more.')
            })
        elif number_of_devices == 0:
            raise exceptions.ValidationError({
                'number_of_devices': _('Please order more then zero!')
            })
        elif number_of_devices < 0:
            raise exceptions.ValidationError({
                'number_of_devices': _('Please pick an order more then zero!')
            })
        return data

    @transaction.atomic
    def create(self, validated_data):
        # Do nothing.
        return validated_data
