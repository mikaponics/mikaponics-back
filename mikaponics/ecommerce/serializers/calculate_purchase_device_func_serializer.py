# -*- coding: utf-8 -*-
import django_rq
from decimal import Decimal
from djmoney.money import Money
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
from foundation.models import User, Product, Shipper, Invoice, InvoiceItem, Store
from foundation.model_resources import find_usable_coupon_for_user

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
    total_before_tax = serializers.FloatField(read_only=True)
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
            'shipping_country',
            'shipping_region',
            'shipping_locality',
            'total_before_tax',
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
        #-----------------#
        # Get our inputs. #
        #-----------------#
        user = self.context.get('by')
        from_ip = self.context.get('from')
        from_ip_is_public = self.context.get('from_is_public')
        default_shipper = Shipper.objects.get(id=MIKAPONICS_DEFAULT_SHIPPER_ID)
        default_store = Store.objects.default_store
        cart = validated_data['cart']
        shipping_country = validated_data.get('shipping_country')
        shipping_region = validated_data.get('shipping_region')

        #--------------------------------#
        # Perform our calculations here. #
        #--------------------------------#
        total_before_tax = 0;
        for product in cart:
            total_before_tax += product.get('totalPrice')
        total_before_tax = Decimal(total_before_tax)

        # Calculate the tax.
        tax = 0
        tax_percent = default_store.get_tax_rate(shipping_country, shipping_region)
        if tax_percent:
            tax_rate = tax_percent / Decimal(100.00)
            tax = total_before_tax * tax_rate
        else:
            tax_percent = Decimal(0.00)
        total_after_tax = total_before_tax + tax

        # # Calculate grand total
        grand_total = total_after_tax

        # Calculate the credit.
        credit = 0
        coupon = find_usable_coupon_for_user(user)
        if coupon:
            credit = coupon.credit

        # Step 1: Apply the credit.
        if credit:
            grand_total -= credit

        # Step 2: Apply the shipping.
        if default_shipper:
            shipping_price = default_shipper.shipping_price
            grand_total += shipping_price.amount

        #----------------------------------#
        # Set our outputs and return them. #
        #----------------------------------#
        validated_data['total_before_tax'] = total_before_tax;
        validated_data['tax'] = tax;
        validated_data['totalAfterTax'] = total_after_tax;
        validated_data['shipping'] = default_shipper.shipping_price.amount
        validated_data['credit'] = credit;
        validated_data['grand_total'] = grand_total;
        validated_data['grand_total_in_cents'] = grand_total * 100;
        return validated_data
