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
from foundation.utils import get_timestamp_of_first_date_for_next_month
from foundation.models import User, Product, Shipper, Invoice, InvoiceItem

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY



class PurchaseSubscriptionRetrieveSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    amount_in_dollars = serializers.FloatField()
    amount_in_cents = serializers.FloatField()
    currency = serializers.CharField()

    # Meta Information.
    class Meta:
        fields = (
            'id',
            'name',
            'amount_in_dollars',
            'amount_in_cents',
            'currency'
        )


class PurchaseSubscriptionUpdateSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    amount_in_dollars = serializers.FloatField()
    amount_in_cents = serializers.FloatField()
    currency = serializers.CharField()

    # Meta Information.
    class Meta:
        fields = (
            'id',
            'name',
            'amount_in_dollars',
            'amount_in_cents',
            'currency'
        )
