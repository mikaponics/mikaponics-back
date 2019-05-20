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
from alert.filters.alert_item_filter import AlertItemFilter
from foundation.models import AlertItem


class AlertItemsListAPIView(generics.ListAPIView):
    serializer_class = AlertItemListSerializer
    # pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanListCreateInstrumentPermission
    )
    # TODO: https://django-oauth-toolkit.readthedocs.io/en/latest/rest-framework/permissions.html#tokenmatchesoasrequirements
    filterset_class = AlertItemFilter

    @transaction.atomic
    def get_queryset(self):
        queryset = AlertItem.objects.filter(user=self.request.user).order_by('-created_at')

        # Take the queryset and apply the joins to increase performance.
        s = self.get_serializer_class()
        return s.setup_eager_loading(self, queryset)
