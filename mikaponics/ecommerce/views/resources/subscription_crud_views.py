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
    SubscriptionRetrieveSerializer,
    SubscriptionUpdateSerializer
)


class SubscriptionAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanListCreateInvoiceItemPermission
    )

    def get(self, request, format=None):
        """
        Return the subscription status information for the authenticated user.
        """
        # Get the user's IP address.
        client_ip, is_routable = get_client_ip(self.request)
        serializer = SubscriptionRetrieveSerializer(request.user)
        serialized_data = serializer.data
        # print("SubscriptionAPIView | OUTPUT:", serialized_data)   # For debugging purposes only.
        return Response(serialized_data)

    def post(self, request, format=None):
        """
        Update the existing "onboarding invoice".
        """
        # Get the user's IP address.
        client_ip, is_routable = get_client_ip(self.request)

        serializer = SubscriptionUpdateSerializer(request.user, data=request.data, context={
            'from': client_ip,
            'from_is_public': is_routable,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()

        serializer = SubscriptionRetrieveSerializer(request.user)
        return Response(serializer.data)
