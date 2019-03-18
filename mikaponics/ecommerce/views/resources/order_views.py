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

from foundation.models import Order
from ecommerce.serializers import (
    OrderRetrieveUpdateBillingAddressSerializer,
    OrderRetrieveUpdateShippingAddressSerializer
)


class OrderRetrieveUpdateBillingAddressAPIView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes= (OAuth2Authentication,)
    serializer_class = OrderRetrieveUpdateBillingAddressSerializer
    # pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanRetrieveUpdateDestroyOrderPermission
    )
    parser_classes = (
        parsers.FormParser,
        parsers.MultiPartParser,
        parsers.JSONParser,
    )
    renderer_classes = (renderers.JSONRenderer,)

    @transaction.atomic
    def put(self, request, pk=None):
        """
        Update
        """
        obj = Order.objects.select_for_update().filter(pk=pk).first()
        if obj is None:
            raise Http404()
        client_ip, is_routable = get_client_ip(self.request)
        self.check_object_permissions(request, obj)  # Validate permissions.
        serializer = OrderRetrieveUpdateBillingAddressSerializer(obj, data=request.data, context={
            'authenticated_by': request.user,
            'authenticated_from': client_ip,
            'authenticated_from_is_public': is_routable,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderRetrieveUpdateShippingAddressAPIView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes= (OAuth2Authentication,)
    serializer_class = OrderRetrieveUpdateShippingAddressSerializer
    # pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanRetrieveUpdateDestroyOrderPermission
    )
    parser_classes = (
        parsers.FormParser,
        parsers.MultiPartParser,
        parsers.JSONParser,
    )
    renderer_classes = (renderers.JSONRenderer,)

    @transaction.atomic
    def put(self, request, pk=None):
        """
        Update
        """
        obj = Order.objects.select_for_update().filter(pk=pk).first()
        if obj is None:
            raise Http404()
        client_ip, is_routable = get_client_ip(self.request)
        self.check_object_permissions(request, obj)  # Validate permissions.
        serializer = OrderRetrieveUpdateShippingAddressSerializer(obj, data=request.data, context={
            'authenticated_by': request.user,
            'authenticated_from': client_ip,
            'authenticated_from_is_public': is_routable,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
