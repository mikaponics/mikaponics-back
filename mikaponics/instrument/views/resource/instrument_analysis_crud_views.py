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

from foundation.models import Instrument, InstrumentAnalysis
from instrument.serializers import (
    InstrumentAnalysisListCreateSerializer,
    InstrumentAnalysisRetrieveUpdateSerializer
)
from foundation.models import InstrumentAnalysis


class InstrumentAnalysisListCreateAPIView(generics.ListCreateAPIView):
    # filter_class = InstrumentFilter
    serializer_class = InstrumentAnalysisListCreateSerializer
    # pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanListCreateInstrumentPermission
    )
    # TODO: https://django-oauth-toolkit.readthedocs.io/en/latest/rest-framework/permissions.html#tokenmatchesoasrequirements

    @transaction.atomic
    def get_queryset(self):
        """
        List
        """
        queryset = InstrumentAnalysis.objects.filter(
            instrument__device__user=self.request.user,
        ).order_by('-created_at')
        return queryset

    @transaction.atomic
    def post(self, request):
        """
        Create
        """
        client_ip, is_routable = get_client_ip(self.request)
        write_serializer = InstrumentAnalysisListCreateSerializer(data=request.data, context={
            'created_by': request.user,
            'created_from': client_ip,
            'created_from_is_public': is_routable,
        })
        write_serializer.is_valid(raise_exception=True)
        analysis = write_serializer.save()
        read_serializer = InstrumentAnalysisRetrieveUpdateSerializer(analysis, many=False, context={
            'created_by': request.user,
            'created_from': client_ip,
            'created_from_is_public': is_routable,
        })
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)


class InstrumentAnalysisRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = InstrumentAnalysisRetrieveUpdateSerializer
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
        skill_set = get_object_or_404(InstrumentAnalysis, slug=slug)
        self.check_object_permissions(request, skill_set)  # Validate permissions.
        serializer = InstrumentAnalysisRetrieveUpdateSerializer(skill_set, many=False)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    @transaction.atomic
    def put(self, request, slug=None):
        """
        Update
        """
        instrument_analysis = get_object_or_404(InstrumentAnalysis, slug=slug)
        self.check_object_permissions(request, instrument_analysis)  # Validate permissions.
        write_serializer = InstrumentAnalysisRetrieveUpdateSerializer(skill_set, data=request.data)
        write_serializer.is_valid(raise_exception=True)
        write_serializer.save()

        read_serializer = InstrumentAnalysisRetrieveUpdateSerializer(instrument_analysis, many=False)
        return Response(
            data=read_serializer.data,
            status=status.HTTP_200_OK
        )
