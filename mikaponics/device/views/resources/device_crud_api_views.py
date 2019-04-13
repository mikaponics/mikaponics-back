# -*- coding: utf-8 -*-
import django_filters
from ipware import get_client_ip
from django_filters import rest_framework as filters
from django.conf.urls import url, include
from django.db import transaction
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status,  parsers, renderers
from rest_framework.response import Response

from device.serializers import (
    DeviceListCreateSerializer,
    DeviceRetrieveUpdateDestroySerializer,
    DeviceProfileSerializer
)
from foundation.models import Device


class DeviceListCreateAPIView(generics.ListCreateAPIView):
    """
    LIST EXAMPLE:
    http get 127.0.0.1:8000/api/devices page==1 \
        Authorization:"Bearer NJKcqxrc7JeuwV87Pm4qa3fn1vc9Gl"

    CREATE EXAMPLE:
    http post 127.0.0.1:8000/api/devices \
        Authorization:"Bearer NJKcqxrc7JeuwV87Pm4qa3fn1vc9Gl" \
        data_interval_in_seconds="1
    """
    # filter_class = DeviceFilter
    serializer_class = DeviceListCreateSerializer
    # pagination_class = StandardResultsSetPagination
    permission_classes = (
        # permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanListCreateDevicePermission
    )
    # TODO: https://django-oauth-toolkit.readthedocs.io/en/latest/rest-framework/permissions.html#tokenmatchesoasrequirements

    @transaction.atomic
    def get_queryset(self):
        """
        List
        """
        queryset = Device.objects.all().order_by('-slug')
        return queryset

    @transaction.atomic
    def post(self, request, format=None):
        """
        Create
        """
        serializer = DeviceListCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DeviceRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DeviceRetrieveUpdateDestroySerializer
    # pagination_class = StandardResultsSetPagination
    permission_classes = (
        # permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanRetrieveUpdateDestroyDevicePermission
    )
    parser_classes = (
        parsers.FormParser,
        parsers.MultiPartParser,
        parsers.JSONParser,
    )
    renderer_classes = (renderers.JSONRenderer,)

    @transaction.atomic
    def get(self, request, slug=None):
        """
        Retrieve
        """
        device = get_object_or_404(Device, slug=slug)
        self.check_object_permissions(request, device)  # Validate permissions.
        serializer = DeviceRetrieveUpdateDestroySerializer(device, many=False)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    @transaction.atomic
    def put(self, request, slug=None):
        """
        Update
        """
        device = get_object_or_404(Device, slug=slug)
        self.check_object_permissions(request, device)  # Validate permissions.
        client_ip, is_routable = get_client_ip(self.request)
        serializer = DeviceRetrieveUpdateDestroySerializer(device, data=request.data, context={
            'authenticated_user': request.user,
            'authenticated_user_from': client_ip,
            'authenticated_user_from_is_public': is_routable,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Refresh the recently updated model.
        device.refresh_from_db()

        # Return our serialized device.
        s = DeviceRetrieveUpdateDestroySerializer(device, many=False, context={
            'authenticated_user': request.user,
            'authenticated_user_from': client_ip,
            'authenticated_user_from_is_public': is_routable,
        })
        return Response(
            data=s.data,
            status=status.HTTP_200_OK
        )

    @transaction.atomic
    def delete(self, request, slug=None):
        """
        Delete
        """
        device = get_object_or_404(Device, slug=slug)
        self.check_object_permissions(request, device)  # Validate permissions.
        device.delete()
        return Response(data=[], status=status.HTTP_200_OK)




class DeviceProfileAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DeviceProfileSerializer
    # pagination_class = StandardResultsSetPagination
    permission_classes = (
        # permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanRetrieveUpdateDestroyDevicePermission
    )

    permission_classes = (
        permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanListCreateWorkInvoicePermission
    )
    parser_classes = (
        parsers.FormParser,
        parsers.MultiPartParser,
        parsers.JSONParser,
    )
    renderer_classes = (renderers.JSONRenderer,)

    @transaction.atomic
    def get(self, request, slug=None):
        """
        Retrieve
        """
        device = get_object_or_404(Device, slug=slug)
        self.check_object_permissions(request, device)  # Validate permissions.
        serializer = DeviceProfileSerializer(device, many=False)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    @transaction.atomic
    def put(self, request, slug=None):
        """
        Update
        """
        device = get_object_or_404(Device, slug=slug)
        self.check_object_permissions(request, device)  # Validate permissions.
        serializer = DeviceProfileSerializer(device, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
