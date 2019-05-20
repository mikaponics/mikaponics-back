# -*- coding: utf-8 -*-
import django_filters
from django_filters import rest_framework as filters
from django.conf.urls import url, include
from django.db import transaction
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status,  parsers, renderers
from rest_framework.response import Response

from alert.serializers import (
    AlertItemListSerializer,
    AlertItemRetrieveSerializer
)
from foundation.models import AlertItem


class AlertItemsListAPIView(generics.ListAPIView):
    # filter_class = InstrumentFilter
    serializer_class = AlertItemListSerializer
    # pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanListCreateInstrumentPermission
    )
    # TODO: https://django-oauth-toolkit.readthedocs.io/en/latest/rest-framework/permissions.html#tokenmatchesoasrequirements

    @transaction.atomic
    def get_queryset(self):
        queryset = AlertItem.objects.filter(user=self.request.user).order_by('-created_at')

        # Take the queryset and apply the joins to increase performance.
        s = self.get_serializer_class()
        return s.setup_eager_loading(self, queryset)


class AlertItemRetrieveAPIView(generics.RetrieveAPIView):
    # filter_class = InstrumentFilter
    serializer_class = AlertItemRetrieveSerializer
    # pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanListCreateInstrumentPermission
    )
    # TODO: https://django-oauth-toolkit.readthedocs.io/en/latest/rest-framework/permissions.html#tokenmatchesoasrequirements

    @transaction.atomic
    def get(self, request, slug=None):
        """
        Retrieve
        """
        obj = get_object_or_404(AlertItem, slug=slug)
        self.check_object_permissions(request, obj)  # Validate permissions.
        serializer = AlertItemRetrieveSerializer(obj, many=False)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )
