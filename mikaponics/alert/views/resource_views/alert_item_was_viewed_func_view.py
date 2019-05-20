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


class AlertItemWasViewedFuncAPIView(generics.RetrieveAPIView):
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
    def post(self, request, slug=None):
        """
        Retrieve
        """
        obj = get_object_or_404(AlertItem, slug=slug)
        self.check_object_permissions(request, obj)  # Validate permissions.
        obj.state = AlertItem.ALERT_ITEM_STATE.READ
        obj.save()
        serializer = AlertItemRetrieveSerializer(obj, many=False)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )
