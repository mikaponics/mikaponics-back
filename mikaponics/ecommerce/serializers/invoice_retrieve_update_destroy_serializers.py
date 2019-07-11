# -*- coding: utf-8 -*-
import logging
import django_rq
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

from ecommerce.tasks import run_send_customer_receipt_email_by_invoice_id_func
from ecommerce.serializers.invoice_item_retrieve_update_destroy_serializers import InvoiceItemRetrieveUpdateDestroySerializer
from foundation.models import Invoice, Product

logger = logging.getLogger(__name__)


def get_todays_date_plus_days(days=0):
    """Returns the current date plus paramter number of days."""
    return timezone.now() + timedelta(days=days)


class InvoiceRetrieveUpdateSerializer(serializers.Serializer):
    state = serializers.CharField(read_only=True, source="get_pretty_state")
    slug = serializers.SlugField(read_only=True)
    absolute_url = serializers.ReadOnlyField(source="get_absolute_url")
    purchased_at = serializers.DateTimeField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    last_modified_at = serializers.DateTimeField(read_only=True)
    due_at = serializers.DateTimeField(read_only=True)
    number = serializers.IntegerField(read_only=True)
    total_before_tax = serializers.FloatField(read_only=True)
    tax = serializers.FloatField(read_only=True)
    tax_percent = serializers.FloatField(read_only=True)
    total_after_tax = serializers.FloatField(read_only=True)
    shipping = serializers.FloatField(read_only=True)
    credit = serializers.FloatField(read_only=True)
    grand_total = serializers.FloatField(read_only=True)

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
    shipping_given_name = serializers.CharField(required=False,allow_blank=True,)
    shipping_last_name = serializers.CharField(required=False,allow_blank=True,)
    shipping_country = serializers.CharField(required=False,allow_blank=True,)
    shipping_region = serializers.CharField(required=False,allow_blank=True,)
    shipping_locality = serializers.CharField(required=False,allow_blank=True,)
    shipping_postal_code = serializers.CharField(required=False,allow_blank=True,)
    shipping_street_address = serializers.CharField(required=False,allow_blank=True,)
    shipping_street_address_extra = serializers.CharField(required=False,allow_blank=True,)
    shipping_postal_code = serializers.CharField(required=False,allow_blank=True,allow_null=True)
    shipping_post_office_box_number = serializers.CharField(required=False,allow_blank=True,)
    shipping_email = serializers.CharField(required=False,allow_blank=True,)
    shipping_telephone = serializers.CharField(required=False,allow_blank=True,)

    items = InvoiceItemRetrieveUpdateDestroySerializer(read_only=True, many=True, source="invoice_items")

    # Meta Information.
    class Meta:
        fields = (
            'state',
            'slug',
            'absolute_url',
            'purchased_at',
            'due_at',
            'created_at',
            'last_modified_at',
            'number',
            'total_before_tax',
            'tax',
            'tax_percent',
            'total_after_tax',
            'shipping',
            'credit',
            'grand_total',

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
            'shipping_given_name',
            'shipping_last_name',
            'shipping_country',
            'shipping_region',
            'shipping_locality',
            'shipping_postal_code',
            'shipping_street_address',
            'shipping_street_address_extra',
            'shipping_postal_code',
            'shipping_post_office_box_number',
            'shipping_email',
            'shipping_telephone',

            'items',
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



class InvoiceRetrieveUpdateBillingAddressSerializer(serializers.Serializer):
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



class InvoiceRetrieveUpdateShippingAddressSerializer(serializers.Serializer):
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


class InvoiceSendEmailSerializer(serializers.Serializer):
    email = serializers.CharField(required=True,allow_blank=False,)

    # Meta Information.
    class Meta:
        fields = (
            'email',
        )

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        email = validated_data.get('email', None)
        invoice = self.context['invoice']
        django_rq.enqueue(run_send_customer_receipt_email_by_invoice_id_func, invoice_id=invoice.id, override_email=email)
        return validated_data
