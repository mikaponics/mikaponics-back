# -*- coding: utf-8 -*-
import django_filters
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasScope
from django.conf import settings
from django.db import transaction
from django.http import Http404
from django_filters import rest_framework as filters
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from django.utils import timezone
from oauth2_provider.models import Application, AbstractApplication, AbstractAccessToken, AccessToken, RefreshToken
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status,  parsers, renderers
from rest_framework.response import Response

from production.serializers.production_retrieve_serializer import ProductionRetrieveSerializer
from production.serializers.production_termination_serializer import ProductionTerminationSerializer
from foundation.models import Production


class ProductionTerminationAPIView(generics.RetrieveUpdateAPIView):
    # serializer_class = ProductionCropRetrieveSerializer
    # pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanRetrieveUpdateDestroyProductionCropPermission
    )

    @transaction.atomic
    def put(self, request, slug=None):
        """
        Update
        """
        object = get_object_or_404(Production, slug=slug)
        self.check_object_permissions(request, object)  # Validate permissions.
        write_serializer = ProductionTerminationSerializer(object, data=request.data, context={
            'authenticated_by': request.user,
            'authenticated_from': request.client_ip,
            'authenticated_from_is_public': request.client_ip_is_routable,
            'was_success': request.data.get("was_success", None)
        })
        write_serializer.is_valid(raise_exception=True)
        write_serializer.save()
        object.refresh_from_db()
        read_serializer = ProductionRetrieveSerializer(object, many=False, context={
            'authenticated_by': request.user,
            'authenticated_from': request.client_ip,
            'authenticated_from_is_public': request.client_ip_is_routable,
        })
        return Response(read_serializer.data, status=status.HTTP_200_OK)
