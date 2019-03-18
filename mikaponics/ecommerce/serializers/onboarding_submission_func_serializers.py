# -*- coding: utf-8 -*-
import logging
import stripe
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

from foundation.models import Invoice, User


logger = logging.getLogger(__name__)


def get_todays_date_plus_days(days=0):
    """Returns the current date plus paramter number of days."""
    return timezone.now() + timedelta(days=days)


class OnboardingSubmissionFuncSerializer(serializers.Serializer):
    # Purchase.
    number_of_devices = serializers.IntegerField(required=True)
    payment_token = serializers.CharField(required=True,allow_blank=False,)
    payment_created_at = serializers.IntegerField(required=True)

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
            'payment_token',
            'payment_created_at',

            # Billing address.
            'billing_given_name',
            'billing_last_name',
            'billing_address_country',
            'billing_address_region',
            'billing_address_locality',
            'billing_postal_code',
            'billing_street_address',
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
                'number_of_devices': _('Cannot invoice more then 50 devices in one invoice, please contact <a href="mailto:info@mikaponics.com">info@mikasoftware.com</a> to invoice more.')
            })
        elif number_of_devices == 0:
            raise exceptions.ValidationError({
                'number_of_devices': _('Please invoice more then zero!')
            })
        elif number_of_devices < 0:
            raise exceptions.ValidationError({
                'number_of_devices': _('Please pick an invoice more then zero!')
            })
        return data

    def process_customer(self, validated_data, context):
        """
        Function will create a customer account on the payment merchant if there
        has no account created previously.
        """
        # Get our variables.
        token = validated_data['payment_token']
        user = context['user']

        # Get the stripe customer ID if we have it.
        customer_id = user.customer_id

        # If we don't have it then create our account now.
        if customer_id is None:
            customer = stripe.Customer.create(
                source=token,
                email=user.email,
            )
            user.customer_id = customer.id
            user.customer_data = customer
            user.save()

        # Return our validated data.
        return validated_data

    def process_product_purchase(self, validated_data, context):
        # print(validated_data) # For debugging purposes.

        # Get variables.
        user = context['user']
        payment_token = validated_data['payment_token']

        # Get our open invoice.
        draft_invoice = user.draft_invoice

        # Set our invoice.
        draft_invoice.number_of_devices = validated_data['number_of_devices']

        draft_invoice.billing_given_name = validated_data['billing_given_name']
        draft_invoice.billing_last_name = validated_data['billing_last_name']
        draft_invoice.billing_country = validated_data['billing_address_country']
        draft_invoice.billing_region = validated_data['billing_address_region']
        draft_invoice.billing_locality = validated_data['billing_address_locality']
        draft_invoice.billing_postal_code = validated_data['billing_postal_code']
        draft_invoice.billing_street_address = validated_data['billing_street_address']
        draft_invoice.billing_post_office_box_number = validated_data['billing_post_office_box_number']
        draft_invoice.billing_email = validated_data['billing_email']
        draft_invoice.billing_telephone = validated_data['billing_telephone']

        draft_invoice.shipping_given_name = validated_data['shipping_given_name']
        draft_invoice.shipping_last_name = validated_data['shipping_last_name']
        draft_invoice.shipping_country = validated_data['shipping_address_country']
        draft_invoice.shipping_region = validated_data['shipping_address_region']
        draft_invoice.shipping_locality = validated_data['shipping_address_locality']
        draft_invoice.shipping_postal_code = validated_data['shipping_postal_code']
        draft_invoice.shipping_street_address = validated_data['shipping_street_address']
        draft_invoice.shipping_postal_code = validated_data['shipping_postal_code']
        draft_invoice.shipping_post_office_box_number = validated_data['shipping_post_office_box_number']
        draft_invoice.shipping_email = validated_data['shipping_email']
        draft_invoice.shipping_telephone = validated_data['shipping_telephone']

        # Extract our bill amount.
        grand_total_in_pennies = draft_invoice.get_grand_total_in_pennies()

        # Perform our charge on `stripe.com`.
        charge = stripe.Charge.create(
            amount=grand_total_in_pennies, # Written in pennies!
            currency=draft_invoice.store.currency,
            description='A Django charge', #TODO: CHANGE NAME.
            customer=user.customer_id,
            shipping={
                "address":{
                    "city": draft_invoice.shipping_locality,
                    "country": draft_invoice.shipping_country,
                    "line1": draft_invoice.shipping_street_address,
                    "line2": draft_invoice.shipping_street_address_extra,
                    "postal_code": draft_invoice.shipping_postal_code,
                    "state": draft_invoice.shipping_region
                },
                "name": draft_invoice.shipping_given_name+" "+draft_invoice.shipping_last_name,
                "phone": draft_invoice.shipping_telephone,
            }
        )

        # # Update our invoice.
        draft_invoice.state = Invoice.ORDER_STATE.PURCHASE_SUCCEEDED
        draft_invoice.stripe_receipt_id = str(charge.id)
        draft_invoice.stripe_receipt_data = charge
        draft_invoice.save()

        # Return our validated data.
        return validated_data

    def process_subscription(self, validated_data, context):
        # Get variables.
        user = context['user']
        draft_invoice = user.draft_invoice

        # If user has not been subscribed, then proceed to do so now.
        if user.subscription_status != User.SUBSCRIPTION_STATUS.ACTIVE:
            # Submit to the payment merchant our subscription request.
            result = stripe.Subscription.create(
                customer=user.customer_id,
                items=[{
                    "plan": user.subscription_plan.payment_plan_id,
                    "quantity": 1,
                },]
            )
            print(result)

            # Update our model object to be saved.
            user.subscription_status = User.SUBSCRIPTION_STATUS.ACTIVE;
            user.subscription_data = result;
            user.save()

        return validated_data

    @transaction.atomic
    def create(self, validated_data):
        validated_data = self.process_customer(validated_data, self.context)
        validated_data = self.process_product_purchase(validated_data, self.context)
        validated_data = self.process_subscription(validated_data, self.context)
        return validated_data
