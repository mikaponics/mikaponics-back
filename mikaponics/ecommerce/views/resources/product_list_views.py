# -*- coding: utf-8 -*-
import django_filters
from ipware import get_client_ip
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasScope
from django.db import transaction
from django.db.models import Q
from django.http import Http404
from django_filters import rest_framework as filters
from django.conf.urls import url, include
from django.utils import timezone
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status,  parsers, renderers
from rest_framework.response import Response

from foundation.models import Product
from ecommerce.serializers import ProductListSerializer


class ProductListAPIView(generics.ListCreateAPIView):
    authentication_classes= (OAuth2Authentication,)
    serializer_class = ProductListSerializer
    # pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanRetrieveUpdateDestroyProductPermission
    )

    def get_queryset(self):
        """
        List
        """
        queryset = Product.objects.filter(
            Q(state=Product.STATE.PUBLISHED)|
            Q(state=Product.STATE.COMING_SOON)
        ).order_by('sort_number')
        return queryset
