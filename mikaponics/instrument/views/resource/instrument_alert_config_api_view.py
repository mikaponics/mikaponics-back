# -*- coding: utf-8 -*-
import django_filters
from django_filters import rest_framework as filters
from django.conf.urls import url, include
from django.db import transaction
from django.shortcuts import get_list_or_404, get_object_or_404
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasScope
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status,  parsers, renderers
from rest_framework.response import Response

from instrument.serializers import InstrumentAlertConfigRetrieveUpdateDestroySerializer
from foundation.models import Instrument


class InstrumentAlertConfigRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes= (OAuth2Authentication,)
    serializer_class = InstrumentAlertConfigRetrieveUpdateDestroySerializer
    # pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanRetrieveUpdateDestroyOrderPermission
    )
    parser_classes = (
        parsers.FormParser,
        parsers.MultiPartParser,
        parsers.JSONParser,
    )
    renderer_classes = (renderers.JSONRenderer,)

    @transaction.atomic
    def get(self, request, pk=None):
        """
        Retrieve
        """
        skill_set = get_object_or_404(Instrument, pk=pk)
        self.check_object_permissions(request, skill_set)  # Validate permissions.
        serializer = InstrumentAlertConfigRetrieveUpdateDestroySerializer(skill_set, many=False)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    @transaction.atomic
    def put(self, request, pk=None):
        """
        Update
        """
        skill_set = get_object_or_404(Instrument, pk=pk)
        self.check_object_permissions(request, skill_set)  # Validate permissions.
        serializer = InstrumentAlertConfigRetrieveUpdateDestroySerializer(skill_set, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
