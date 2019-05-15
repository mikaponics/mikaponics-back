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
    parser_classes = (
        parsers.FormParser,
        parsers.MultiPartParser,
        parsers.JSONParser,
    )
    renderer_classes = (renderers.JSONRenderer,)

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
        client_ip, is_routable = get_client_ip(self.request)
        self.check_object_permissions(request, request.user)  # Validate permissions.
        grow_system = request.data.get("grow_system")
        write_serializer = ProductionInspectionCreateSerializer(data=request.data, context={
            'authenticated_by': request.user,
            'authenticated_from': client_ip,
            'authenticated_from_is_public': is_routable,
            'did_pass': did_pass,
        })
        write_serializer.is_valid(raise_exception=True)
        validated_data = write_serializer.save()
        production = validated_data['production']
        read_serializer = ProductionInspectionRetrieveSerializer(production, many=False, context={
            'authenticated_by': request.user,
            'authenticated_from': client_ip,
            'authenticated_from_is_public': is_routable,
        })
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)
