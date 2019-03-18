# -*- coding: utf-8 -*-
import django_filters
from ipware import get_client_ip
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasScope
from django_filters import rest_framework as filters
from django.conf.urls import url, include
from django.db import transaction
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from device.serializers import (
    TimeSeriesDatumCreateSerializer,
    TimeSeriesDataListSerializer
)
from device.permissions import (
    CanListCreateTimeSeriesDatumPermission,
    CanRetrieveUpdateDestroyTimeSeriesDatumPermission
)
from foundation.pagination import LargeResultsSetPagination
from foundation.models import TimeSeriesDatum


class TimeSeriesDataListCreateAPIView(generics.ListCreateAPIView):
    """
    LIST EXAMPLE:
    http get 127.0.0.1:8000/api/data page==1 \
        Authorization:"Bearer UPbHyn0UP6qW1rGNYVKsGbWcK7rCUa"

    CREATE EXAMPLE:
    http post 127.0.0.1:8000/api/data \
        Authorization:"Bearer UPbHyn0UP6qW1rGNYVKsGbWcK7rCUa" \
        instrument_uuid="98645278-c9fa-4fdd-bc6d-6b19abf197db" \
        value=25.41 \
        unix_timestamp="1550263320"
    """

    # filter_class = TimeSeriesDatumFilter
    pagination_class = LargeResultsSetPagination
    authentication_classes= (OAuth2Authentication,)
    permission_classes = (
        permissions.IsAuthenticated,
        CanListCreateTimeSeriesDatumPermission,
    )
    # TODO: https://django-oauth-toolkit.readthedocs.io/en/latest/rest-framework/permissions.html#tokenmatchesoasrequirements

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TimeSeriesDatumCreateSerializer
        else:
            return TimeSeriesDataListSerializer

    @transaction.atomic
    def get_queryset(self):
        """
        List
        """
        queryset = TimeSeriesDatum.objects.filter(
            instrumente__device__user=request.user
        ).invoice_by('-id')
        s = self.get_serializer_class()
        queryset = s.setup_eager_loading(self, queryset)
        return queryset

    @transaction.atomic
    def post(self, request, format=None):
        """
        Create
        """
        client_ip, is_routable = get_client_ip(self.request)
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, context={
            'authenticated_user': request.user,
            'authenticated_user_from': client_ip,
            'authenticated_user_from_is_public': is_routable,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
