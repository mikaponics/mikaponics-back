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
    InstrumentAlertListSerializer
)
from foundation.models import InstrumentAlert


class InstrumentAlertsListAPIView(generics.ListAPIView):
    # filter_class = InstrumentFilter
    serializer_class = InstrumentAlertListSerializer
    # pagination_class = StandardResultsSetPagination
    permission_classes = (
        # permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanListCreateInstrumentPermission
    )
    # TODO: https://django-oauth-toolkit.readthedocs.io/en/latest/rest-framework/permissions.html#tokenmatchesoasrequirements

    @transaction.atomic
    def get_queryset(self):
        queryset = InstrumentAlert.objects.all()

        # Take the queryset and apply the joins to increase performance.
        s = self.get_serializer_class()
        return s.setup_eager_loading(self, queryset)
