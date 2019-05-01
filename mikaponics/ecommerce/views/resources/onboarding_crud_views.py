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
from foundation.models import Product, Shipper, Invoice, InvoiceItem
from ecommerce.serializers import (
    OnboardingRetrieveSerializer,
    OnboardingUpdateSerializer
)


class OnboardingAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OnboardingRetrieveSerializer
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

        # Get or create the draft invoice of the user.
        draft_invoice = request.user.draft_invoice

        # Fetch the default product & subscription which we will apply to
        # the onboarding purchase.
        default_product = Product.objects.get(id=MIKAPONICS_DEFAULT_PRODUCT_ID)
        default_shipper = Shipper.objects.get(id=MIKAPONICS_DEFAULT_SHIPPER_ID)

        serializer = OnboardingRetrieveSerializer(draft_invoice, many=False, context={
            'authenticated_by': request.user,
            'authenticated_from': client_ip,
            'authenticated_from_is_public': is_routable,
            'draft_invoice': draft_invoice,
            'default_product': default_product,
            'default_shipper': default_shipper,
            'default_subscription': {
                'amount': Money(settings.STRIPE_MONTHLY_PLAN_AMOUNT, settings.STRIPE_MONTHLY_PLAN_CURRENCY),
                'id': settings.STRIPE_MONTHLY_PLAN_ID
            }
        })
        return Response(serializer.data)

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

        serializer = OnboardingUpdateSerializer(draft_invoice, data=request.data, many=False, context={
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

        serializer = OnboardingRetrieveSerializer(draft_invoice, many=False, context={
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
