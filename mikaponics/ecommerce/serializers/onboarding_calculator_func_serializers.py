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

from foundation.constants import (
    MIKAPONICS_DEFAULT_PRODUCT_ID,
    MIKAPONICS_DEFAULT_SUBSCRIPTION_ID,
    MIKAPONICS_DEFAULT_SHIPPER_ID
)
from foundation.models import Product, SubscriptionPlan, Shipper, InvoiceItem


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
        """
        Function will create our onboarding invoice calculation.
        """
        # Fetch the default product & subscription which we will apply to
        # the onboarding purchase.
        default_product = Product.objects.get(id=MIKAPONICS_DEFAULT_PRODUCT_ID)
        default_shipper = Shipper.objects.get(id=MIKAPONICS_DEFAULT_SHIPPER_ID)
        default_subscription = SubscriptionPlan.objects.get(id=MIKAPONICS_DEFAULT_SUBSCRIPTION_ID)

        # Get our user object from the context.
        user = self.context['user']

        # Get our open invoice for the user.
        draft_invoice = user.draft_invoice

        # Update our open invoice with how many devices the user wants to purchase.
        draft_invoice.number_of_devices = validated_data['number_of_devices']
        draft_invoice.shipper = default_shipper
        draft_invoice.shipping_country = validated_data['shipping_address_country']
        draft_invoice.shipping_region = validated_data['shipping_address_region']
        draft_invoice.save()
        draft_invoice.invalidate('total')

        # Update our user to be enrolled in the subscription plan.
        user.subscription_plan = default_subscription
        user.save()

        # Add our purchase.
        InvoiceItem.objects.update_or_create(
            invoice=draft_invoice,
            product=default_product,
            defaults={
                'invoice': draft_invoice,
                'product': default_product,
                'number_of_products': validated_data['number_of_devices'],
                'product_price': default_product.price,
            }
        )

        # Generate our calculation based on the invoice variables set.
        total_calc = draft_invoice.total;

        # Create our calculation output.
        validated_data['calculation'] = {
            'monthlyFee': str(default_subscription.amount),
            'numberOfDevices': draft_invoice.number_of_devices,
            'pricePerDevice': str(default_product.price),
            'totalBeforeTax': str(draft_invoice.total_before_tax),
            'tax': str(draft_invoice.tax),
            'totalAfterTax': str(draft_invoice.total_after_tax),
            'shipping': str(draft_invoice.shipping),
            'credit': str(draft_invoice.credit),
            'grandTotal': str(draft_invoice.grand_total),
            'grandTotalInCents': int(total_calc['grand_total_in_cents']),
        };

        # # For debugging purposes only.
        # print("---------")
        # print(total_calc)
        # print("---------")
        # print(validated_data)
        # print("---------")

        # Return our calculations.
        return validated_data
