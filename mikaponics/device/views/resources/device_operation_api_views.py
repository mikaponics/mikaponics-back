# -*- coding: utf-8 -*-
from ipware import get_client_ip
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasScope
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from device.permissions import (
   CanListCreateDevicePermission,
   CanRetrieveUpdateDestroyDevicePermission
)
from device.serializers import DeviceActivateOperationSerializer
from device.serializers import DeviceInstrumentSetTimeSeriesDatumeOperationSerializer


class DeviceActivateOperationAPIView(generics.CreateAPIView):
    """
    Example:
    http post 127.0.0.1:8000/api/device-operations/activate \
         Authorization:"Bearer NJKcqxrc7JeuwV87Pm4qa3fn1vc9Gl" \
         uuid="774f5188-9f4d-4c95-a5ac-389304384a33"
    """
    serializer_class = DeviceActivateOperationSerializer
    authentication_classes= (OAuth2Authentication,)
    permission_classes = (
        permissions.IsAuthenticated,
        # CanListCreateDevicePermission
    )

    def post(self, request, format=None):
        """
        Create
        """
        client_ip, is_routable = get_client_ip(self.request)
        serializer = DeviceActivateOperationSerializer(data=request.data, context={
            'authenticate_user': request.user,
            'authenticate_user_from': client_ip,
            'authenticate_user_from_is_public': is_routable,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)




class DeviceInstrumentSetTimeSeriesDatumeOperationAPIView(generics.CreateAPIView):
    """
    Example:
    http post 127.0.0.1:8000/api/device-operations/submit-data \
         Authorization:"Bearer NJKcqxrc7JeuwV87Pm4qa3fn1vc9Gl" \
         uuid="774f5188-9f4d-4c95-a5ac-389304384a33" \
         type_of=1 \
         value=666 \
         utc_timestamp=1550200823
    """
    serializer_class = DeviceInstrumentSetTimeSeriesDatumeOperationSerializer
    permission_classes = (
        # permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanListCreateWorkOrderPermission
    )

    def post(self, request, format=None):
        """
        Create
        """
        client_ip, is_routable = get_client_ip(self.request)
        serializer = DeviceInstrumentSetTimeSeriesDatumeOperationSerializer(data=request.data, context={
            'authenticate_user': request.user,
            'authenticate_user_from': client_ip,
            'authenticate_user_from_is_public': is_routable,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
