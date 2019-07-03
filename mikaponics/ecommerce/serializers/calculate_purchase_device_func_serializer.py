# -*- coding: utf-8 -*-
import django_rq
import stripe
import logging
from djmoney.money import Money
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

from ecommerce.tasks import (
    run_send_customer_receipt_email_by_invoice_id_func,
    run_send_staff_receipt_email_by_invoice_id_func
)
from foundation.utils import (
    get_timestamp_of_first_date_for_next_month,
    get_first_date_for_next_month
)
from foundation.models import User, Product, Shipper, Invoice, InvoiceItem

logger = logging.getLogger(__name__)


from foundation.constants import (
    MIKAPONICS_DEFAULT_PRODUCT_ID,
    MIKAPONICS_DEFAULT_SUBSCRIPTION_ID,
    MIKAPONICS_DEFAULT_SHIPPER_ID
)

class CalculatePurchaseDeviceFuncSerializer(serializers.Serializer):
    # INPUT.
    cart = serializers.JSONField(write_only=True, required=True, allow_null=False)
    shipping_country = serializers.CharField(write_only=True, required=True, allow_null=False)
    shipping_region = serializers.CharField(write_only=True, required=True, allow_null=False)
    shipping_locality = serializers.CharField(write_only=True, required=True, allow_null=False)

    # OUTPUT.
    totalBeforeTax = serializers.FloatField(read_only=True)
    tax = serializers.FloatField(read_only=True)
    totalAfterTax = serializers.FloatField(read_only=True)
    shipping = serializers.FloatField(read_only=True)
    credit = serializers.FloatField(read_only=True)
    grand_total = serializers.FloatField(read_only=True)
    grand_total_in_cents = serializers.IntegerField(read_only=True)

    # Meta Information.
    class Meta:
        fields = (
            'cart',
            'totalBeforeTax',
            'tax',
            'totalAfterTax',
            'shipping',
            'credit',
            'grand_total',
            'grand_total_in_cents',
        )

    def create(self, validated_data):
        """
        Override this function to include extra functionality.
        """
        from_ip = self.context.get('from')
        from_ip_is_public = self.context.get('from_is_public')
        default_shipper = Shipper.objects.get(id=MIKAPONICS_DEFAULT_SHIPPER_ID)
        cart = validated_data['cart']

        print(cart) #TODO: PROCESSING.

        validated_data['totalBeforeTax'] = 666;
        validated_data['tax'] = 666;
        validated_data['totalAfterTax'] = 666;
        validated_data['shipping'] = 666;
        validated_data['credit'] = 666;
        validated_data['grand_total'] = 666;
        validated_data['grand_total_in_cents'] = 666;

        return validated_data
