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


from production.serializers.production_crop_create_serializer import ProductionCropCreateSerializer
from production.serializers.production_crop_list_serializer import ProductionCropListSerializer
from production.serializers.production_crop_retrieve_serializer import ProductionCropRetrieveSerializer
from production.serializers.production_crop_update_serializer import ProductionCropUpdateSerializer
from foundation.models import ProductionCrop


class ProductionCropRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    # serializer_class = ProductionCropRetrieveSerializer
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
        client_ip, is_routable = get_client_ip(self.request)
        object = get_object_or_404(ProductionCrop, slug=slug)
        self.check_object_permissions(request, object)  # Validate permissions.
        serializer = ProductionCropRetrieveSerializer(object, many=False, context={
            'authenticated_by': request.user,
            'authenticated_from': client_ip,
            'authenticated_from_is_public': is_routable
        })
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    @transaction.atomic
    def put(self, request, slug=None):
        """
        Update
        """
        client_ip, is_routable = get_client_ip(self.request)
        object = get_object_or_404(ProductionCrop, slug=slug)
        self.check_object_permissions(request, object)  # Validate permissions.
        print(request.data)
        serializer = ProductionCropUpdateSerializer(object, data=request.data, context={
            'authenticated_by': request.user,
            'authenticated_from': client_ip,
            'authenticated_from_is_public': is_routable,
            'state_at_finish': request.data.get('state_at_finish', None),
            'harvest_at_finish': request.data.get('harvest_at_finish', None),
        })
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.save()
        serializer = ProductionCropRetrieveSerializer(validated_data['production_crop'], many=False, context={
            'authenticated_by': request.user,
            'authenticated_from': client_ip,
            'authenticated_from_is_public': is_routable
        })
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )
