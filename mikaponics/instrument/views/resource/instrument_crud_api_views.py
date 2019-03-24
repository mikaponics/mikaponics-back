# -*- coding: utf-8 -*-
import django_filters
from django_filters import rest_framework as filters
from django.conf.urls import url, include
from django.db import transaction
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status,  parsers, renderers
from rest_framework.response import Response

from instrument.serializers import (
    InstrumentListSerializer,
    InstrumentRetrieveUpdateSerializer
)
from foundation.models import Instrument


class InstrumentListAPIView(generics.ListAPIView):
    """
    LIST EXAMPLE:
    http get 127.0.0.1:8000/api/devices page==1 \
        Authorization:"Bearer NJKcqxrc7JeuwV87Pm4qa3fn1vc9Gl"

    CREATE EXAMPLE:
    http post 127.0.0.1:8000/api/devices \
        Authorization:"Bearer NJKcqxrc7JeuwV87Pm4qa3fn1vc9Gl" \
        data_interval_in_seconds="1
    """
    # filter_class = InstrumentFilter
    serializer_class = InstrumentListSerializer
    # pagination_class = StandardResultsSetPagination
    permission_classes = (
        # permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanListCreateInstrumentPermission
    )
    # TODO: https://django-oauth-toolkit.readthedocs.io/en/latest/rest-framework/permissions.html#tokenmatchesoasrequirements

    @transaction.atomic
    def get_queryset(self):
        """
        List
        """
        queryset = Instrument.objects.all()
        return queryset


class InstrumentRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = InstrumentRetrieveUpdateSerializer
    # pagination_class = StandardResultsSetPagination
    permission_classes = (
        # permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanRetrieveUpdateDestroyInstrumentPermission
    )

    @transaction.atomic
    def get(self, request, slug=None):
        """
        Retrieve
        """
        skill_set = get_object_or_404(Instrument, slug=slug)
        self.check_object_permissions(request, skill_set)  # Validate permissions.
        serializer = InstrumentRetrieveUpdateSerializer(skill_set, many=False)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    @transaction.atomic
    def put(self, request, slug=None):
        """
        Update
        """
        skill_set = get_object_or_404(Instrument, slug=slug)
        self.check_object_permissions(request, skill_set)  # Validate permissions.
        serializer = InstrumentRetrieveUpdateSerializer(skill_set, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
