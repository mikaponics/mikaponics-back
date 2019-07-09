# -*- coding: utf-8 -*-
import django_filters
from django_filters import rest_framework as filters
from django.conf.urls import url, include
from django.db import transaction
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status,  parsers, renderers
from rest_framework.response import Response

from device.serializers import DeviceAuthorizeSerializer
from foundation.models import Device


class DeviceAuthorizeAPIView(generics.CreateAPIView):
    # filter_class = DeviceFilter
    serializer_class = DeviceAuthorizeSerializer
    # pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanListCreateDevicePermission
    )
    # TODO: https://django-oauth-toolkit.readthedocs.io/en/latest/rest-framework/permissions.html#tokenmatchesoasrequirements

    @transaction.atomic
    def post(self, request, format=None):
        """
        Create
        """
        serializer = DeviceAuthorizeSerializer(data=request.data, context={
            'authenticated_user': request.user,
            'authenticated_user_from': request.client_ip,
            'authenticated_user_from_is_public': request.client_ip_is_routable,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
