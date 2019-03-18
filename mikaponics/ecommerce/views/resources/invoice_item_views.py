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

from foundation.models import InvoiceItem
from ecommerce.serializers import (
    InvoiceItemRetrieveUpdateDestroySerializer
)


# class InvoiceItemListCreateAPIView(generics.ListCreateAPIView):
#     serializer_class = InvoiceItemListCreateSerializer
#     pagination_class = StandardResultsSetPagination
#     permission_classes = (
#         permissions.IsAuthenticated,
#         IsAuthenticatedAndIsActivePermission,
#         CanListCreateInvoiceItemPermission
#     )
#
#     def get_queryset(self):
#         """
#         List
#         """
#         queryset = InvoiceItem.objects.all().invoice_by('text')
#         return queryset
#
#     def post(self, request, format=None):
#         """
#         Create
#         """
#         client_ip, is_routable = get_client_ip(self.request)
#         serializer = InvoiceItemListCreateSerializer(data=request.data, context={
#             'created_by': request.user,
#             'created_from': client_ip,
#             'created_from_is_public': is_routable,
#             'franchise': request.tenant
#         })
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


class InvoiceItemRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes= (OAuth2Authentication,)
    serializer_class = InvoiceItemRetrieveUpdateDestroySerializer
    # pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanRetrieveUpdateDestroyInvoiceItemPermission
    )
    parser_classes = (
        parsers.FormParser,
        parsers.MultiPartParser,
        parsers.JSONParser,
    )
    renderer_classes = (renderers.JSONRenderer,)

    def get(self, request, pk=None):
        """
        Retrieve
        """
        obj = InvoiceItem.objects.select_for_update().filter(pk=pk).first()
        if obj is None:
            raise Http404()
        client_ip, is_routable = get_client_ip(self.request)
        self.check_object_permissions(request, obj)  # Validate permissions.
        serializer = InvoiceItemRetrieveUpdateDestroySerializer(obj, many=False)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    @transaction.atomic
    def put(self, request, pk=None):
        """
        Update
        """
        obj = InvoiceItem.objects.select_for_update().filter(pk=pk).first()
        if obj is None:
            raise Http404()
        client_ip, is_routable = get_client_ip(self.request)
        self.check_object_permissions(request, obj)  # Validate permissions.
        serializer = InvoiceItemRetrieveUpdateDestroySerializer(obj, data=request.data, context={
            'authenticated_by': request.user,
            'authenticated_from': client_ip,
            'authenticated_from_is_public': is_routable,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def delete(self, request, pk=None):
        """
        Delete
        """
        obj = InvoiceItem.objects.select_for_update().filter(pk=pk).first()
        if obj is None:
            raise Http404()
        client_ip, is_routable = get_client_ip(self.request)
        self.check_object_permissions(request, obj)  # Validate permissions.
        serializer = InvoiceItemRetrieveUpdateDestroySerializer(obj, data=request.data, context={
            'authenticated_by': request.user,
            'authenticated_from': client_ip,
            'authenticated_from_is_public': is_routable,
        })
        serializer.is_valid(raise_exception=True)
        serializer.delete()
        return Response(serializer.data, status=status.HTTP_200_OK)
