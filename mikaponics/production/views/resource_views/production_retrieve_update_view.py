# -*- coding: utf-8 -*-
import django_filters
from ipware import get_client_ip
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

from production.serializers.production_create_serializer import ProductionCreateSerializer
from production.serializers.production_list_serializer import ProductionListSerializer
from production.serializers.production_retrieve_serializer import ProductionRetrieveSerializer
from production.serializers.production_update_serializer import ProductionUpdateSerializer
from foundation.models import Production


class ProductionRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ProductionRetrieveSerializer
    # pagination_class = StandardResultsSetPagination
    permission_classes = (
        # permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanRetrieveUpdateDestroyProductionPermission
    )

    # @transaction.atomic
    def get(self, request, slug=None):
        """
        Retrieve
        """
        object = get_object_or_404(Production, slug=slug)
        self.check_object_permissions(request, object)  # Validate permissions.
        serializer = ProductionRetrieveSerializer(object, many=False)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    @transaction.atomic
    def put(self, request, slug=None):
        """
        Update
        """
        """
        Update
        """
        client_ip, is_routable = get_client_ip(self.request)
        object = get_object_or_404(Production, slug=slug)
        self.check_object_permissions(request, object)  # Validate permissions.
        write_serializer = ProductionUpdateSerializer(object, data=request.data, context={
            'authenticated_by': request.user,
            'authenticated_from': client_ip,
            'authenticated_from_is_public': is_routable,
        })
        write_serializer.is_valid(raise_exception=True)
        write_serializer.save()
        object.refresh_from_db()
        read_serializer = ProductionUpdateSerializer(object, many=False, context={
            'authenticated_by': request.user,
            'authenticated_from': client_ip,
            'authenticated_from_is_public': is_routable,
        })
        return Response(read_serializer.data, status=status.HTTP_200_OK)
