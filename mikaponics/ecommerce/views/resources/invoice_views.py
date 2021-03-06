# -*- coding: utf-8 -*-
import django_filters
from ipware import get_client_ip
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasScope
from django.db import transaction
from django.http import Http404
from django_filters import rest_framework as filters
from django.conf.urls import url, include
from django.utils import timezone
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status,  parsers, renderers
from rest_framework.response import Response

from foundation.models import Invoice
from ecommerce.serializers import (
    InvoiceListCreateSerializer,
    InvoiceRetrieveUpdateSerializer,
    InvoiceRetrieveUpdateBillingAddressSerializer,
    InvoiceRetrieveUpdateShippingAddressSerializer,
    InvoiceSendEmailSerializer
)


class InvoiceListCreateAPIView(generics.ListCreateAPIView):
    authentication_classes= (OAuth2Authentication,)
    serializer_class = InvoiceListCreateSerializer
    # pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanRetrieveUpdateDestroyInvoicePermission
    )

    def get_queryset(self):
        """
        List
        """
        queryset = Invoice.objects.filter(user=self.request.user).order_by('-created_at')
        return queryset

    def post(self, request, format=None):
        """
        Create
        """
        client_ip, is_routable = get_client_ip(self.request)
        serializer = InvoiceListCreateSerializer(data=request.data, context={
            'created_by': request.user,
            'created_from': client_ip,
            'created_from_is_public': is_routable,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class InvoiceRetrieveDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes= (OAuth2Authentication,)
    serializer_class = InvoiceRetrieveUpdateSerializer
    # pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanRetrieveUpdateDestroyInvoicePermission
    )

    @transaction.atomic
    def get(self, request, slug=None):
        """
        Retrieve
        """
        obj = Invoice.objects.select_for_update().filter(slug=slug).first()
        if obj is None:
            raise Http404()

        client_ip, is_routable = get_client_ip(self.request)
        self.check_object_permissions(request, obj)  # Validate permissions.

        serializer = InvoiceRetrieveUpdateSerializer(obj, many=False)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    @transaction.atomic
    def put(self, request, pk=None):
        """
        Update
        """
        obj = Invoice.objects.select_for_update().filter(pk=pk).first()
        if obj is None:
            raise Http404()

        client_ip, is_routable = get_client_ip(self.request)
        self.check_object_permissions(request, obj)  # Validate permissions.

        serializer = InvoiceRetrieveUpdateSerializer(obj, data=request.data, context={
            'authenticated_by': request.user,
            'authenticated_from': client_ip,
            'authenticated_from_is_public': is_routable,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class InvoiceRetrieveUpdateBillingAddressAPIView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes= (OAuth2Authentication,)
    serializer_class = InvoiceSendEmailSerializer
    # pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanRetrieveUpdateDestroyInvoicePermission
    )

    @transaction.atomic
    def put(self, request, pk=None):
        """
        Update
        """
        obj = Invoice.objects.select_for_update().filter(pk=pk).first()
        if obj is None:
            raise Http404()
        client_ip, is_routable = get_client_ip(self.request)
        self.check_object_permissions(request, obj)  # Validate permissions.
        serializer = InvoiceRetrieveUpdateBillingAddressSerializer(obj, data=request.data, context={
            'authenticated_by': request.user,
            'authenticated_from': client_ip,
            'authenticated_from_is_public': is_routable,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class InvoiceRetrieveUpdateShippingAddressAPIView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes= (OAuth2Authentication,)
    serializer_class = InvoiceRetrieveUpdateShippingAddressSerializer
    # pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanRetrieveUpdateDestroyInvoicePermission
    )

    @transaction.atomic
    def put(self, request, pk=None):
        """
        Update
        """
        obj = Invoice.objects.select_for_update().filter(pk=pk).first()
        if obj is None:
            raise Http404()
        client_ip, is_routable = get_client_ip(self.request)
        self.check_object_permissions(request, obj)  # Validate permissions.
        serializer = InvoiceRetrieveUpdateShippingAddressSerializer(obj, data=request.data, context={
            'authenticated_by': request.user,
            'authenticated_from': client_ip,
            'authenticated_from_is_public': is_routable,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class InvoiceSendEmailAPIView(generics.UpdateAPIView):
    authentication_classes= (OAuth2Authentication,)
    serializer_class = InvoiceRetrieveUpdateSerializer
    # pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanRetrieveUpdateDestroyInvoicePermission
    )

    @transaction.atomic
    def put(self, request, slug=None):
        """
        Update
        """
        obj = Invoice.objects.select_for_update().filter(slug=slug).first()
        if obj is None:
            raise Http404()

        client_ip, is_routable = get_client_ip(self.request)
        self.check_object_permissions(request, obj)  # Validate permissions.

        serializer = InvoiceSendEmailSerializer(obj, data=request.data, context={
            'invoice': obj,
            'authenticated_by': request.user,
            'authenticated_from': client_ip,
            'authenticated_from_is_public': is_routable,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
