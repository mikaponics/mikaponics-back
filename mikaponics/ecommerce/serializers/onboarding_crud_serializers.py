# -*- coding: utf-8 -*-
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


class OnboardingUpdateSerializer(serializers.Serializer):
    # PURCHASE QUANTITY
    quantity = serializers.IntegerField(required=True, write_only=True)

    # BILLING INFORMATION
    billing_given_name = serializers.CharField(required=True,allow_blank=False,)
    billing_last_name = serializers.CharField(required=True,allow_blank=False,)
    billing_country = serializers.CharField(required=True,allow_blank=False,)
    billing_region = serializers.CharField(required=True,allow_blank=False,)
    billing_locality = serializers.CharField(required=True,allow_blank=False,)
    billing_postal_code = serializers.CharField(required=True,allow_blank=False,)
    billing_street_address = serializers.CharField(required=True,allow_blank=False,)
    billing_postal_code = serializers.CharField(required=True,allow_blank=False,)
    billing_post_office_box_number = serializers.CharField(required=False,allow_blank=True, allow_null=True)
    billing_email = serializers.CharField(required=True,allow_blank=False,)
    billing_telephone = serializers.CharField(required=True,allow_blank=False,)

    # SHIPPING INFORMATION
    shipping_given_name = serializers.CharField(required=True,allow_blank=False,)
    shipping_last_name = serializers.CharField(required=True,allow_blank=False,)
    shipping_country = serializers.CharField(required=True,allow_blank=False,)
    shipping_region = serializers.CharField(required=True,allow_blank=False,)
    shipping_locality = serializers.CharField(required=True,allow_blank=False,)
    shipping_postal_code = serializers.CharField(required=True,allow_blank=False,)
    shipping_street_address = serializers.CharField(required=True,allow_blank=False,)
    shipping_postal_code = serializers.CharField(required=True,allow_blank=False,)
    shipping_post_office_box_number = serializers.CharField(required=False,allow_blank=True, allow_null=True)
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

    # PAYMENT MERCHANT
    payment_token = serializers.CharField(required=False, allow_blank=True,)
    payment_created_at = serializers.IntegerField(required=False)

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


            # PAYMENT MERCHANT
            'payment_token',
            'payment_created_at',
        )

    def validate_quantity(self, data):
        if data is None:
            raise exceptions.ValidationError(_("Please pick number greater then zero."))
        if data < 1:
            raise exceptions.ValidationError(_("Please pick number greater then zero."))
        return data

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        # Fetch the default product & subscription which we will apply to
        # the onboarding purchase.
        default_product = self.context['default_product']
        default_shipper = self.context['default_shipper']
        default_subscription = self.context['default_subscription']

        # PURCHASE QUANTITY
        quantity = validated_data.get('quantity')

        # BILLING INFORMATION
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

        # SHIPPING INFORMATION
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

        # Update our open invoice with our default shipper.
        instance.shipper = default_shipper

        # SAVING OUR SUBMISSION
        instance.save()

        # CHECKOUT FINANCIAL INFORMATION
        instance.invalidate('total')

        # Get our user object from the context.
        user = self.context['authenticated_by']

        # Add or update our purchase.
        item, was_created = InvoiceItem.objects.update_or_create(
            invoice=instance,
            product=default_product,
            defaults={
                'invoice': instance,
                'product': default_product,
                'description': default_product.description,
                'quantity': quantity,
                'unit_price': default_product.price,
                'total_price': default_product.price * quantity
            }
        )

        # Generate our calculation based on the invoice variables set.
        total_calc = instance.total;

        # PAYMENT MERCHANT
        token = validated_data.get('payment_token', None)
        if token:
            validated_data = self.process_customer(validated_data, self.context)
            validated_data = self.process_product_purchase(validated_data, self.context)
            validated_data = self.process_subscription(validated_data, self.context)

        # Return our validated data.
        return validated_data

    def process_customer(self, validated_data, context):
        """
        Function will create a customer account on the payment merchant if there
        has no account created previously.
        """
        # print(validated_data) # For debugging purposes only.

        # Get our variables.
        token = validated_data['payment_token']
        user = context['authenticated_by']

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
                'non_field_errors': [
                    str(e),
                ]
            })


        # Return our validated data.
        return validated_data

    def process_product_purchase(self, validated_data, context):
        # print(validated_data) # For debugging purposes.

        # Get variables.
        user = context['authenticated_by']
        payment_token = validated_data['payment_token']

        # Get our open invoice.
        draft_invoice = user.draft_invoice

        # Refresh the latest data.
        draft_invoice.refresh_from_db()

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
        draft_invoice.payment_merchant_receipt_id = str(charge.id)
        draft_invoice.payment_merchant_receipt_data = charge
        draft_invoice.save()

        # Return our validated data.
        return validated_data

    def process_subscription(self, validated_data, context):
        # Get variables.
        user = context['authenticated_by']

        # Refresh the latest data from the database.
        user.refresh_from_db()

        default_product = self.context['default_product']
        default_subscription = self.context['default_subscription']

        # Special thanks:
        # (1) https://stripe.com/docs/billing/subscriptions/billing-cycle
        # (2) https://stripe.com/docs/billing/subscriptions/trials#combine-trial-anchor

        # If user has not been subscribed, then proceed to do so now.
        if user.subscription_status != User.SUBSCRIPTION_STATUS.ACTIVE:
            # Submit to the payment merchant our subscription request.
            result = stripe.Subscription.create(
                customer=user.customer_id,
                items=[{
                    "plan": default_subscription['id'],
                    "quantity": 1,
                },],
                billing_cycle_anchor=get_timestamp_of_first_date_for_next_month()
            )
            print("PAYMENT MERCHANT SUBSCRIPTION RESULTS\n", result) # For debugging purposes only.

            # Update our model object to be saved.
            user.subscription_status = User.SUBSCRIPTION_STATUS.ACTIVE;
            user.subscription_data = result;
            user.save()

        return validated_data
