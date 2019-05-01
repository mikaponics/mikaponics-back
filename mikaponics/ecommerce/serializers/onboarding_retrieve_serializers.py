# -*- coding: utf-8 -*-
import django_rq
import stripe
import logging
from datetime import datetime, timedelta
from dateutil import tz
from djmoney.money import Money
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
    run_send_staff_receipt_email_by_invoice_id_func,
    run_send_staff_user_onboarded_email_by_user_id_func
)
from foundation.utils import get_timestamp_of_first_date_for_next_month
from foundation.models import User, Product, Shipper, Invoice, InvoiceItem

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


class OnboardingRetrieveSerializer(serializers.Serializer):
    # PURCHASE QUANTITY
    quantity = serializers.SerializerMethodField()

    # BILLING INFORMATION
    billing_given_name = serializers.CharField(required=True,allow_blank=False,)
    billing_last_name = serializers.CharField(required=True,allow_blank=False,)
    billing_country = serializers.CharField(required=True,allow_blank=False,)
    billing_region = serializers.CharField(required=True,allow_blank=False,)
    billing_locality = serializers.CharField(required=True,allow_blank=False,)
    billing_postal_code = serializers.CharField(required=True,allow_blank=False,)
    billing_street_address = serializers.CharField(required=True,allow_blank=False,)
    billing_postal_code = serializers.CharField(required=True,allow_blank=False,)
    billing_post_office_box_number = serializers.CharField(required=False,allow_blank=True,)
    billing_email = serializers.CharField(required=True,allow_blank=False,)
    billing_telephone = serializers.CharField(required=True,allow_blank=False,)

    # SHIPPING INFORMATION
    is_shipping_different_then_billing = serializers.BooleanField(required=False)
    shipping_given_name = serializers.CharField(required=True,allow_blank=False,)
    shipping_last_name = serializers.CharField(required=True,allow_blank=False,)
    shipping_country = serializers.CharField(required=True,allow_blank=False,)
    shipping_region = serializers.CharField(required=True,allow_blank=False,)
    shipping_locality = serializers.CharField(required=True,allow_blank=False,)
    shipping_postal_code = serializers.CharField(required=True,allow_blank=False,)
    shipping_street_address = serializers.CharField(required=True,allow_blank=False,)
    shipping_postal_code = serializers.CharField(required=True,allow_blank=False,)
    shipping_post_office_box_number = serializers.CharField(required=False,allow_blank=True,)
    shipping_email = serializers.CharField(required=True,allow_blank=False,)
    shipping_telephone = serializers.CharField(required=True,allow_blank=False,)

    # CHECKOUT FINANCIAL INFORMATION
    state = serializers.CharField(read_only=True, source="get_pretty_state")
    slug = serializers.SlugField(read_only=True)
    absolute_url = serializers.ReadOnlyField(source="get_absolute_url")
    purchased_at = serializers.DateTimeField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    last_modified_at = serializers.DateTimeField(read_only=True)
    due_at = serializers.DateTimeField(read_only=True)
    number = serializers.IntegerField(read_only=True)
    total_before_tax = serializers.CharField(read_only=True)
    tax = serializers.CharField(read_only=True)
    tax_percent = serializers.FloatField(read_only=True)
    total_after_tax = serializers.CharField(read_only=True)
    shipping = serializers.CharField(read_only=True)
    credit = serializers.CharField(read_only=True)
    grand_total = serializers.CharField(read_only=True)
    calculation = serializers.SerializerMethodField()

    # MISC
    authenticated_user_email = serializers.SerializerMethodField()  # Used for debugging purposes only!

    # Meta Information.
    class Meta:
        fields = (
            # # 'invoice',
            # # 'product',

            # PURCHASE QUANTITY
            'quantity',

            # BILLING INFORMATION
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

            # SHIPPING INFORMATION
            'is_shipping_different_then_billing',
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

            # CHECKOUT FINANCIAL INFORMATION
            'state',
            'slug',
            'absolute_url',
            'purchased_at',
            'created_at',
            'last_modified_at',
            'number',
            'total_before_tax',
            'tax_percent',
            'tax',
            'total_after_tax',
            'shipping',
            'credit',
            'grand_total',
            # 'description',
            # 'unit_price',
            # 'total_price'
            'calculation',

            # MISC
            'authenticated_user_email'
        )

    def get_quantity(self, obj):
        try:
            item = InvoiceItem.objects.get(
                invoice=self.context['draft_invoice'],
                product=self.context['default_product']
            )
            return item.quantity
        except Exception as e:
            print("OnboardingRetrieveSerializer - get_quantity - exception:", e)
            return 0

    def get_calculation(self, obj):
        try:
            # Generate our calculation based on the invoice variables set.
            total_calc = obj.total;

            # Fetch the default product & subscription which we will apply to
            # the onboarding purchase.
            default_product = self.context['default_product']
            # default_shipper = self.context['default_shipper']
            default_subscription = self.context['default_subscription']
            default_subscription_amount = default_subscription['amount']

            # Create our calculation output.
            return {
                'description': default_product.description,
                'monthlyFee': str(default_subscription_amount),
                'quantity':self.get_quantity(obj),
                'pricePerDevice': str(default_product.price),
                'totalBeforeTax': str(obj.total_before_tax),
                'tax': str(obj.tax),
                'totalAfterTax': str(obj.total_after_tax),
                'shipping': str(obj.shipping),
                'credit': str(obj.credit),
                'grandTotal': str(obj.grand_total),
                'grandTotalInCents': int(total_calc['grand_total_in_cents']),
            };
        except Exception as e:
            print("OnboardingRetrieveSerializer - get_calculation - exception:", e)
            return None

    def get_monthly_fee(self, obj):
        try:
            default_subscription = self.context['default_subscription']
            return str(default_subscription.amount)
        except Exception as e:
            print("OnboardingRetrieveSerializer - get_monthly_fee - exception:", e)
            return Money(0, settings.MIKAPONICS_BACKEND_DEFAULT_MONEY_CURRENCY)

    def get_authenticated_user_email(self, obj):
        """
        Used for debugging purposes only!
        """
        try:
            return self.context['authenticated_by'].email
        except Exception as e:
            print("OnboardingRetrieveSerializer - get_authenticated_user_email - exception:", e)
            return None
