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

from production.filters.production_inspection_filter import ProductionInspectionFilter
from production.serializers.production_inspection_create_serializer import ProductionInspectionCreateSerializer
from production.serializers.production_inspection_list_serializer import ProductionInspectionListSerializer
from production.serializers.production_inspection_retrieve_serializer import ProductionInspectionRetrieveSerializer
from foundation.models import ProductionInspection


class ProductionInspectionListCreateAPIView(generics.ListCreateAPIView):
    filterset_class = ProductionInspectionFilter
    authentication_classes= (OAuth2Authentication,)
    serializer_class = ProductionInspectionListSerializer
    # pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanRetrieveUpdateDestroyInvoicePermission
    )

    def get_queryset(self):
        """
        Get list data.
        """
        queryset = ProductionInspection.objects.filter(
            production__user=self.request.user,
        ).order_by('-created_at')
        return queryset

    @transaction.atomic
    def post(self, request):
        """
        Update
        """
        self.check_object_permissions(request, request.user)  # Validate permissions.
        write_serializer = ProductionInspectionCreateSerializer(data=request.data, context={
            'authenticated_by': request.user,
            'authenticated_from': request.client_ip,
            'authenticated_from_is_public': request.client_ip_is_routable,
            'did_pass': request.data.get("did_pass", None),
        });
        write_serializer.is_valid(raise_exception=True)
        production_inspection = write_serializer.save()
        print(production_inspection)
        read_serializer = ProductionInspectionRetrieveSerializer(production_inspection, many=False, context={
            'authenticated_by': request.user,
            'authenticated_from': request.client_ip,
            'authenticated_from_is_public': request.client_ip_is_routable,
        })
        print(read_serializer)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)
