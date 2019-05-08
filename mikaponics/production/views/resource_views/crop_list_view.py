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

from production.serializers.crop_list_serializer import CropListSerializer
from foundation.models import Crop


class CropFilter(filters.FilterSet):
    type_of = filters.NumberFilter(field_name="type_of")

    class Meta:
        model = Crop
        fields = ['type_of']


class CropListAPIView(generics.ListAPIView):
    authentication_classes= (OAuth2Authentication,)
    serializer_class = CropListSerializer
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
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CropFilter

    def get_queryset(self):
        """
        Get list data.
        """
        queryset = Crop.objects.order_by('order_number')
        return queryset
