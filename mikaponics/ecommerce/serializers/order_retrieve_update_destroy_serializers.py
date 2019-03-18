# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db.models import Q, Prefetch, Sum
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator

from foundation.models import Order, Product


logger = logging.getLogger(__name__)


def get_todays_date_plus_days(days=0):
    """Returns the current date plus paramter number of days."""
    return timezone.now() + timedelta(days=days)


class OrderRetrieveUpdateBillingAddressSerializer(serializers.Serializer):
    billing_given_name = serializers.CharField(required=False,allow_blank=True,)
    billing_last_name = serializers.CharField(required=False,allow_blank=True,)
    billing_country = serializers.CharField(required=False,allow_blank=True,)
    billing_region = serializers.CharField(required=False,allow_blank=True,)
    billing_locality = serializers.CharField(required=False,allow_blank=True,)
    billing_postal_code = serializers.CharField(required=False,allow_blank=True,)
    billing_street_address = serializers.CharField(required=False,allow_blank=True,)
    billing_postal_code = serializers.CharField(required=False,allow_blank=True,)
    billing_post_office_box_number = serializers.CharField(required=False,allow_blank=True,)
    billing_email = serializers.CharField(required=False,allow_blank=True,)
    billing_telephone = serializers.CharField(required=False,allow_blank=True,)

    # Meta Information.
    class Meta:
        fields = (
            'billing_given_name',
            'billing_last_name',
            'billing_country',
            'billing_region',
            'billing_locality',
            'billing_postal_code',
            'billing_street_address',
            'billing_postal_code',
            'billing_post_office_box_number',
            'billing_email',
            'billing_telephone',
        )

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        instance.billing_given_name = validated_data.get('billing_given_name', instance.billing_given_name)
        instance.billing_last_name = validated_data.get('billing_last_name', instance.billing_last_name)
        instance.billing_country = validated_data.get('billing_country', instance.billing_country)
        instance.billing_region = validated_data.get('billing_region', instance.billing_region)
        instance.billing_locality = validated_data.get('billing_locality', instance.billing_locality)
        instance.billing_postal_code = validated_data.get('billing_postal_code', instance.billing_postal_code)
        instance.billing_street_address = validated_data.get('billing_street_address', instance.billing_street_address)
        instance.billing_postal_code = validated_data.get('billing_postal_code', instance.billing_postal_code)
        instance.billing_post_office_box_number = validated_data.get('billing_post_office_box_number', instance.billing_post_office_box_number)
        instance.billing_email = validated_data.get('billing_email', instance.billing_email)
        instance.billing_telephone = validated_data.get('billing_telephone', instance.billing_telephone)
        instance.save()
        return validated_data



class OrderRetrieveUpdateShippingAddressSerializer(serializers.Serializer):
    shipping_given_name = serializers.CharField(required=False,allow_blank=True,)
    shipping_last_name = serializers.CharField(required=False,allow_blank=True,)
    shipping_country = serializers.CharField(required=False,allow_blank=True,)
    shipping_region = serializers.CharField(required=False,allow_blank=True,)
    shipping_locality = serializers.CharField(required=False,allow_blank=True,)
    shipping_postal_code = serializers.CharField(required=False,allow_blank=True,)
    shipping_street_address = serializers.CharField(required=False,allow_blank=True,)
    shipping_postal_code = serializers.CharField(required=False,allow_blank=True,)
    shipping_post_office_box_number = serializers.CharField(required=False,allow_blank=True,)
    shipping_email = serializers.CharField(required=False,allow_blank=True,)
    shipping_telephone = serializers.CharField(required=False,allow_blank=True,)

    # Meta Information.
    class Meta:
        fields = (
            'shipping_given_name',
            'shipping_last_name',
            'shipping_country',
            'shipping_region',
            'shipping_locality',
            'shipping_postal_code',
            'shipping_street_address',
            'shipping_postal_code',
            'shipping_post_office_box_number',
            'shipping_email',
            'shipping_telephone',
        )

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        instance.shipping_given_name = validated_data.get('shipping_given_name', instance.shipping_given_name)
        instance.shipping_last_name = validated_data.get('shipping_last_name', instance.shipping_last_name)
        instance.shipping_country = validated_data.get('shipping_country', instance.shipping_country)
        instance.shipping_region = validated_data.get('shipping_region', instance.shipping_region)
        instance.shipping_locality = validated_data.get('shipping_locality', instance.shipping_locality)
        instance.shipping_postal_code = validated_data.get('shipping_postal_code', instance.shipping_postal_code)
        instance.shipping_street_address = validated_data.get('shipping_street_address', instance.shipping_street_address)
        instance.shipping_postal_code = validated_data.get('shipping_postal_code', instance.shipping_postal_code)
        instance.shipping_post_office_box_number = validated_data.get('shipping_post_office_box_number', instance.shipping_post_office_box_number)
        instance.shipping_email = validated_data.get('shipping_email', instance.shipping_email)
        instance.shipping_telephone = validated_data.get('shipping_telephone', instance.shipping_telephone)
        instance.save()
        return validated_data
