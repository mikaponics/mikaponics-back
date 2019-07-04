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
from foundation.models import User, Product, Shipper, Invoice, InvoiceItem

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


class PurchaseProcessSerializer(serializers.Serializer):
    # --- INPUT ---
    # PAYMENT MERCHANT
    payment_receipt = serializers.JSONField(required=True, allow_null=False, write_only=True)

    # SHOPPING CART
    cart = serializers.JSONField(required=True, allow_null=False, write_only=True)

    # BILLING INFORMATION
    billing_given_name = serializers.CharField(required=True,allow_blank=False, write_only=True,)
    billing_last_name = serializers.CharField(required=True,allow_blank=False, write_only=True,)
    billing_country = serializers.CharField(required=True,allow_blank=False, write_only=True,)
    billing_region = serializers.CharField(required=True,allow_blank=False, write_only=True,)
    billing_locality = serializers.CharField(required=True,allow_blank=False, write_only=True,)
    billing_postal_code = serializers.CharField(required=True,allow_blank=False, write_only=True,)
    billing_street_address = serializers.CharField(required=True,allow_blank=False, write_only=True,)
    billing_postal_code = serializers.CharField(required=True,allow_blank=False, write_only=True,)
    billing_post_office_box_number = serializers.CharField(required=False,allow_blank=True, allow_null=True, write_only=True,)
    billing_email = serializers.CharField(required=True,allow_blank=False, write_only=True,)
    billing_telephone = serializers.CharField(required=True,allow_blank=False, write_only=True,)

    # SHIPPING INFORMATION
    is_shipping_different_then_billing = serializers.BooleanField(required=False, allow_null=True, write_only=True,)
    shipping_given_name = serializers.CharField(required=False, allow_null=True, allow_blank=True, write_only=True,)
    shipping_last_name = serializers.CharField(required=False, allow_null=True, allow_blank=True, write_only=True,)
    shipping_country = serializers.CharField(required=False, allow_null=True, allow_blank=True, write_only=True,)
    shipping_region = serializers.CharField(required=False, allow_null=True, allow_blank=True, write_only=True,)
    shipping_locality = serializers.CharField(required=False, allow_null=True, allow_blank=True, write_only=True,)
    shipping_postal_code = serializers.CharField(required=False, allow_null=True, allow_blank=True, write_only=True,)
    shipping_street_address = serializers.CharField(required=False, allow_null=True, allow_blank=True, write_only=True,)
    shipping_postal_code = serializers.CharField(required=False, allow_null=True, allow_blank=True, write_only=True,)
    shipping_post_office_box_number = serializers.CharField(required=False, allow_null=True,  allow_blank=True, write_only=True,)
    shipping_email = serializers.CharField(required=False, allow_null=True, allow_blank=True, write_only=True,)
    shipping_telephone = serializers.CharField(required=False, allow_null=True, allow_blank=True, write_only=True,)

    # --- OUTPUT ---
    invoice_slug = serializers.SlugField(allow_null=False, read_only=True)
    invoice_receipt = serializers.JSONField(allow_null=False, read_only=True)

    # Meta Information.
    class Meta:
        fields = (
            # --- INPUT ---
            # PAYMENT MERCHANT
            'payment_receipt',

            # SHOPPING CART
            'cart',

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

            # --- OUTPUT ---
            'invoice_slug',
            'invoice_receipt'
        )

    def validate_payment_receipt(self, value):
        if value.get('id'):
            return value
        raise exceptions.ValidationError(_("This JSON is missing the payment token (ID) value."))

    def validate_shipping_given_name(self, value):
        if self.context['is_shipping_different_then_billing']:
            if value is None or value == '':
                raise exceptions.ValidationError(_("This value cannot be left blank."))
        return value

    def validate_shipping_last_name(self, value):
        if self.context['is_shipping_different_then_billing']:
            if value is None or value == '':
                raise exceptions.ValidationError(_("This value cannot be left blank."))
        return value

    def validate_shipping_country(self, value):
        if self.context['is_shipping_different_then_billing']:
            if value is None or value == '':
                raise exceptions.ValidationError(_("This value cannot be left blank."))
        return value

    def validate_shipping_region(self, value):
        if self.context['is_shipping_different_then_billing']:
            if value is None or value == '':
                raise exceptions.ValidationError(_("This value cannot be left blank."))
        return value

    def validate_shipping_locality(self, value):
        if self.context['is_shipping_different_then_billing']:
            if value is None or value == '':
                raise exceptions.ValidationError(_("This value cannot be left blank."))
        return value

    def validate_shipping_postal_code(self, value):
        if self.context['is_shipping_different_then_billing']:
            if value is None or value == '':
                raise exceptions.ValidationError(_("This value cannot be left blank."))
        return value

    def validate_shipping_street_address(self, value):
        if self.context['is_shipping_different_then_billing']:
            if value is None or value == '':
                raise exceptions.ValidationError(_("This value cannot be left blank."))
        return value

    def validate_shipping_postal_code(self, value):
        if self.context['is_shipping_different_then_billing']:
            if value is None or value == '':
                raise exceptions.ValidationError(_("This value cannot be left blank."))
        return value

    def validate_shipping_post_office_box_number(self, value):
        if self.context['is_shipping_different_then_billing']:
            if value is None or value == '':
                raise exceptions.ValidationError(_("This value cannot be left blank."))
        return value

    def validate_shipping_email(self, value):
        if self.context['is_shipping_different_then_billing']:
            if value is None or value == '':
                raise exceptions.ValidationError(_("This value cannot be left blank."))
        return value

    def validate_shipping_telephon(eself, value):
        if self.context['is_shipping_different_then_billing']:
            if value is None or value == '':
                raise exceptions.ValidationError(_("This value cannot be left blank."))
        return value

    def update(self, user, validated_data):
        """
        Override this function to include extra functionality.
        """
        # --- INPUT ---
        draft_invoice = user.draft_invoice
        payment_receipt = validated_data.get('payment_receipt') # PAYMENT MERCHANT
        payment_token = payment_receipt.get('id')
        payment_created_at = payment_receipt.get('created')
        cart = validated_data.get('cart')  # SHOPPING CART

        # Clear any financials that may have been done previously on this draft invoice.
        draft_invoice.invalidate('total')

        # BILLING INFORMATION
        draft_invoice.billing_given_name = validated_data.get('billing_given_name', draft_invoice.billing_given_name)
        draft_invoice.billing_last_name = validated_data.get('billing_last_name', draft_invoice.billing_last_name)
        draft_invoice.billing_country = validated_data.get('billing_country', draft_invoice.billing_country)
        draft_invoice.billing_region = validated_data.get('billing_region', draft_invoice.billing_region)
        draft_invoice.billing_locality = validated_data.get('billing_locality', draft_invoice.billing_locality)
        draft_invoice.billing_postal_code = validated_data.get('billing_postal_code', draft_invoice.billing_postal_code)
        draft_invoice.billing_street_address = validated_data.get('billing_street_address', draft_invoice.billing_street_address)
        draft_invoice.billing_postal_code = validated_data.get('billing_postal_code', draft_invoice.billing_postal_code)
        draft_invoice.billing_post_office_box_number = validated_data.get('billing_post_office_box_number', draft_invoice.billing_post_office_box_number)
        draft_invoice.billing_email = validated_data.get('billing_email', draft_invoice.billing_email)
        draft_invoice.billing_telephone = validated_data.get('billing_telephone', draft_invoice.billing_telephone)

        # SHIPPING INFORMATION
        draft_invoice.shipping_given_name = validated_data.get('shipping_given_name', draft_invoice.shipping_given_name)
        draft_invoice.shipping_last_name = validated_data.get('shipping_last_name', draft_invoice.shipping_last_name)
        draft_invoice.shipping_country = validated_data.get('shipping_country', draft_invoice.shipping_country)
        draft_invoice.shipping_region = validated_data.get('shipping_region', draft_invoice.shipping_region)
        draft_invoice.shipping_locality = validated_data.get('shipping_locality', draft_invoice.shipping_locality)
        draft_invoice.shipping_postal_code = validated_data.get('shipping_postal_code', draft_invoice.shipping_postal_code)
        draft_invoice.shipping_street_address = validated_data.get('shipping_street_address', draft_invoice.shipping_street_address)
        draft_invoice.shipping_postal_code = validated_data.get('shipping_postal_code', draft_invoice.shipping_postal_code)
        draft_invoice.shipping_post_office_box_number = validated_data.get('shipping_post_office_box_number', draft_invoice.shipping_post_office_box_number)
        draft_invoice.shipping_email = validated_data.get('shipping_email', draft_invoice.shipping_email)
        draft_invoice.shipping_telephone = validated_data.get('shipping_telephone', draft_invoice.shipping_telephone)

        draft_invoice.save() # Save latest data for the invoice which was populated above.

        # CART
        calculation = self.process_invoice_items(draft_invoice, cart)

        # PAYMENT MERCHANT - PURCHASE
        self.process_customer(user, payment_token)
        self.process_purchase(draft_invoice, user, payment_token)

        # Return our validated data.
        validated_data['invoice_slug'] = draft_invoice.slug
        validated_data['invoice_receipt'] = calculation

        # Clean up after ourselves and then return our validated data.
        user.invalidate("draft_invoice")
        return validated_data

    def process_invoice_items(self, draft_invoice, cart):
        """
        Function will iterate through the cart the user sent us and we
        will create our `InvoiceItem` objects from them to add to our
        `Invoice` object.
        """
        for item in cart:
            # Find our product.
            product = Product.objects.filter(slug=item.get('slug')).first()

            # Add or update our purchase.
            item, was_created = InvoiceItem.objects.update_or_create(
                invoice=draft_invoice,
                product=product,
                defaults={
                    'invoice': draft_invoice,
                    'product': product,
                    'description': product.description,
                    'quantity': item.get('quantity'),
                    'unit_price': product.price,
                    'total_price': product.price * item.get('quantity')
                }
            )

        # Generate our calculation based on the invoice variables set.
        return draft_invoice.total;

    def process_customer(self, user, payment_token):
        """
        Function will create a customer account on the payment merchant if there
        has no account created previously.
        """
        # Get the stripe customer ID if we have it.
        customer_id = user.customer_id

        # If we don't have it then create our account now.
        try:
            if customer_id is None:
                customer = stripe.Customer.create(
                    source=payment_token,
                    email=user.email,
                )
                user.customer_id = customer.id
                user.customer_data = customer
                user.save()
        except Exception as e:
            raise exceptions.ValidationError({
                'process_customer | non_field_errors': [str(e),]
            })

    def process_purchase(self, draft_invoice, user, payment_token):
        # Extract our bill amount.
        grand_total_in_pennies = draft_invoice.get_grand_total_in_pennies()

        # Perform our charge on `stripe.com`.
        charge = stripe.Charge.create(
            amount=grand_total_in_pennies, # Written in pennies!
            currency=draft_invoice.store.currency,
            description='Mikaponics Device Purchase',
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

        # Update our invoice.
        draft_invoice.state = Invoice.ORDER_STATE.PURCHASE_SUCCEEDED
        draft_invoice.payment_merchant_receipt_id = str(charge.id)
        draft_invoice.payment_merchant_receipt_data = charge
        draft_invoice.save()

        # Claim our coupon if there was one used.
        if draft_invoice.coupon:
            draft_invoice.coupon.claim()

        # Send our activation email to the user.
        django_rq.enqueue(run_send_customer_receipt_email_by_invoice_id_func, invoice_id=draft_invoice.id)
        django_rq.enqueue(run_send_staff_receipt_email_by_invoice_id_func, invoice_id=draft_invoice.id)
