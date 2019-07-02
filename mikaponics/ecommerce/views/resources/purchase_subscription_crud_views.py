# -*- coding: utf-8 -*-
import django_filters
from djmoney.money import Money
from ipware import get_client_ip
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasScope
from django.conf import settings
from django.db import transaction
from django.http import Http404
from django_filters import rest_framework as filters
from django.conf.urls import url, include
from django.utils import timezone
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status,  parsers, renderers
from rest_framework.response import Response

from foundation.constants import (
    MIKAPONICS_DEFAULT_PRODUCT_ID,
    MIKAPONICS_DEFAULT_SUBSCRIPTION_ID,
    MIKAPONICS_DEFAULT_SHIPPER_ID
)
from foundation.models import Store, Product, Shipper, Invoice, InvoiceItem
from ecommerce.serializers import (
    PurchaseSubscriptionRetrieveSerializer,
    PurchaseSubscriptionUpdateSerializer
)


class PurchaseSubscriptionAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PurchaseSubscriptionRetrieveSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanListCreateInvoiceItemPermission
    )

    def get(self, request, format=None):
        """
        Get existing or create new "onboarding invoice" if it was not created.
        """
        # Get the user's IP address.
        client_ip, is_routable = get_client_ip(self.request)
        serializer = PurchaseSubscriptionRetrieveSerializer(data={
            'product_id': settings.STRIPE_MONTHLY_PLAN_ID,
            'amount_in_dollars': float(settings.STRIPE_MONTHLY_PLAN_AMOUNT),
            'amount_in_cents': float(settings.STRIPE_MONTHLY_PLAN_AMOUNT) * 100,
            'currency': settings.STRIPE_MONTHLY_PLAN_CURRENCY,
        })
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data
        # print("PurchaseSubscriptionAPIView | OUTPUT:", serialized_data)   # For debugging purposes only.
        return Response(serialized_data)

    def post(self, request, format=None):
        """
        Update the existing "onboarding invoice".
        """
        # Get the user's IP address.
        client_ip, is_routable = get_client_ip(self.request)

        # Get or create the draft invoice of the user.
        draft_invoice = request.user.draft_invoice

        # Fetch the default product & subscription which we will apply to
        # the onboarding purchase.
        default_product = Product.objects.get(id=MIKAPONICS_DEFAULT_PRODUCT_ID)
        default_shipper = Shipper.objects.get(id=MIKAPONICS_DEFAULT_SHIPPER_ID)

        serializer = PurchaseSubscriptionUpdateSerializer(draft_invoice, data=request.data, many=False, context={
            'authenticated_by': request.user,
            'authenticated_from': client_ip,
            'authenticated_from_is_public': is_routable,
            'draft_invoice': draft_invoice,
            'default_product': default_product,
            'default_shipper': default_shipper,
            'default_subscription': {
                'amount': Money(settings.STRIPE_MONTHLY_PLAN_AMOUNT, settings.STRIPE_MONTHLY_PLAN_CURRENCY),
                'id': settings.STRIPE_MONTHLY_PLAN_ID
            },
            'is_shipping_different_then_billing': request.data.get('is_shipping_different_then_billing', False)
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()

        serializer = PurchaseSubscriptionRetrieveSerializer(draft_invoice, many=False, context={
            'authenticated_by': request.user,
            'authenticated_from': client_ip,
            'authenticated_from_is_public': is_routable,
            'draft_invoice': draft_invoice,
            'default_product': default_product,
            'default_subscription': {
                'amount': Money(settings.STRIPE_MONTHLY_PLAN_AMOUNT, settings.STRIPE_MONTHLY_PLAN_CURRENCY),
                'id': settings.STRIPE_MONTHLY_PLAN_ID
            }
        })
        return Response(serializer.data)
