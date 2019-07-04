# -*- coding: utf-8 -*-
import django_filters
import stripe
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
from foundation.models import User, Store, Product, Shipper, Invoice, InvoiceItem
from ecommerce.serializers import PurchaseProcessSerializer
stripe.api_key = settings.STRIPE_SECRET_KEY


class PurchaseAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanListCreateInvoiceItemPermission
    )

    @transaction.atomic
    def post(self, request, format=None):
        """
        Update the existing "onboarding invoice".
        """
        # Get the user's IP address.
        client_ip, is_routable = get_client_ip(self.request)

        serializer = PurchaseProcessSerializer(request.user, data=request.data, context={
            'by': request.user,
            'from': client_ip,
            'from_is_public': is_routable,
            'is_shipping_different_then_billing': request.data.get('is_shipping_different_then_billing', False)
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
