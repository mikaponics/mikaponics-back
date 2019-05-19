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
from django.utils.translation import ugettext_lazy as _
from oauth2_provider.models import Application, AbstractApplication, AbstractAccessToken, AccessToken, RefreshToken
from rest_framework import generics
from rest_framework import exceptions
from rest_framework import authentication, viewsets, permissions, status,  parsers, renderers
from rest_framework.response import Response

from production.serializers.production_inspection_retrieve_serializer import ProductionInspectionRetrieveSerializer
from foundation.models import Production, ProductionInspection, ProductionCropInspection, CropLifeCycleStage


class ProductionInspectionRetrieveOrCreateDefaultDraftAPIView(generics.RetrieveAPIView):
    """
    Convenience API endpoint used to either (1) return a "ProductionInspection"
    object with the `draft` state or (2) create an object with the `draft`
    state.
    """
    authentication_classes= (OAuth2Authentication,)
    serializer_class = ProductionInspectionRetrieveSerializer
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

    @transaction.atomic
    def get(self, request, slug=None):
        """
        Get
        """
        client_ip, is_routable = get_client_ip(self.request)
        self.check_object_permissions(request, request.user)  # Validate permissions.

        production = Production.objects.filter(slug=slug).first()
        if production is None:
            raise exceptions.ValidationError(_('The slug is not valid!!'))

        # Either fetch our draft inspection or create a new one.
        default_draft_inspection, was_created = ProductionInspection.objects.get_or_create(
            production__slug=slug,
            state=ProductionInspection.STATE.DRAFT,
            defaults={
                'production': production,
                'state': ProductionInspection.STATE.DRAFT,
                'created_by': request.user,
                'created_from': client_ip,
                'created_from_is_public': is_routable,
                'last_modified_by': request.user,
                'last_modified_from': client_ip,
                'last_modified_from_is_public': is_routable,
            }
        )

        # If we created our default inspection then we need to create the
        # accompanying individual crop inspection objects.
        if was_created:
            for production_crop in production.crops.all().order_by('id'):
                ProductionCropInspection.objects.create(
                    production_inspection=default_draft_inspection,
                    production_crop=production_crop,
                    state=ProductionCropInspection.STATE.DRAFT,
                    stage=production_crop.stage,
                    created_by=request.user,
                    created_from=client_ip,
                    created_from_is_public=is_routable,
                    last_modified_by=request.user,
                    last_modified_from=client_ip,
                    last_modified_from_is_public=is_routable,
                )

        # Serialize our object to JSON data.
        read_serializer = ProductionInspectionRetrieveSerializer(default_draft_inspection, many=False, context={
            'authenticated_by': request.user,
            'authenticated_from': client_ip,
            'authenticated_from_is_public': is_routable,
        })

        # Return our results.
        return Response(
            data = read_serializer.data,
            status = status.HTTP_201_CREATED if was_created else status.HTTP_200_OK
        )
