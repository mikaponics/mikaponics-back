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
stripe.api_key = settings.STRIPE_SECRET_KEY



class SubscriptionRetrieveSerializer(serializers.Serializer):
    """
    Serializer returns the subscription status information for the users account
    this information includes costs of the subscription if it would occure.
    """

    def to_representation(self, user):
        return {
            'id': settings.STRIPE_MONTHLY_PLAN_ID,
            'name': settings.STRIPE_MONTHLY_PLAN_NAME,
            'amount_in_dollars': float(settings.STRIPE_MONTHLY_PLAN_AMOUNT),
            'amount_in_cents': float(settings.STRIPE_MONTHLY_PLAN_AMOUNT) * 100,
            'first_payment_timestamp': get_timestamp_of_first_date_for_next_month(),
            'first_payment_date': get_first_date_for_next_month(),
            'currency': settings.STRIPE_MONTHLY_PLAN_CURRENCY,
            'status': user.subscription_status,
            'pretty_status': user.get_pretty_subscription_status()
        }


class SubscriptionUpdateSerializer(serializers.Serializer):
    payment_token = serializers.CharField()

    # Meta Information.
    class Meta:
        fields = (
            'payment_token',
        )

    def update(self, user, validated_data):
        """
        Override this function to include extra functionality.
        """
        # PAYMENT MERCHANT
        token = validated_data.get('payment_token', None)
        if token:
            validated_data = self.process_customer(user, validated_data, self.context)
            validated_data = self.process_subscription(user, validated_data, self.context)

        return validated_data

    def process_customer(self, user, validated_data, context):
        """
        Function will create a customer account on the payment merchant if there
        has no account created previously.
        """
        # print(validated_data) # For debugging purposes only.

        # Get our variables.
        token = validated_data['payment_token']

        # Get the stripe customer ID if we have it.
        customer_id = user.customer_id

        # If we don't have it then create our account now.
        try:
            if customer_id is None:
                customer = stripe.Customer.create(
                    source=token,
                    email=user.email,
                )
                user.customer_id = customer.id
                user.customer_data = customer
                user.save()
        except Exception as e:
            raise exceptions.ValidationError({
                'non_field_errors': [str(e),]
            })

        # Return our validated data.
        return validated_data

    def process_subscription(self, user, validated_data, context):
        # Refresh the latest data from the database.
        user.refresh_from_db()

        # Special thanks:
        # (1) https://stripe.com/docs/billing/subscriptions/billing-cycle
        # (2) https://stripe.com/docs/billing/subscriptions/trials#combine-trial-anchor

        # If user has not been subscribed, then proceed to do so now.
        if user.subscription_status != User.SUBSCRIPTION_STATUS.ACTIVE:
            # Submit to the payment merchant our subscription request.
            result = stripe.Subscription.create(
                customer=user.customer_id,
                items=[{
                    "plan": settings.STRIPE_MONTHLY_PLAN_ID,
                    "quantity": 1,
                },],
                billing_cycle_anchor=get_timestamp_of_first_date_for_next_month()
            )
            print("PAYMENT MERCHANT SUBSCRIPTION RESULTS\n", result) # For debugging purposes only.

            # Update our model object to be saved.
            user.subscription_status = User.SUBSCRIPTION_STATUS.ACTIVE
            user.subscription_start_date = get_first_date_for_next_month()
            user.subscription_data = result
            user.subscription_id = result['id']
            user.save()

        return validated_data
