# -*- coding: utf-8 -*-
import django_filters
from ipware import get_client_ip
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasScope
from django.conf import settings
from django.db.models import Q
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

from production.serializers.problem_data_sheet_list_serializer import ProblemDataSheetListSerializer
from foundation.models import ProblemDataSheet


class ProblemDataSheetFilter(filters.FilterSet):
    def enhanced_type_of_filter(self, name, value):
        """
        Filter method used to INCLUDE the "other" option along with the filtered
        option to filter by. This is important because we want the "Other"
        option to always be listed regardless of time being filtered.
        """
        return self.filter(
            Q(type_of=ProblemDataSheet.TYPE_OF.NONE)|
            Q(type_of=value)
        )

    type_of = filters.NumberFilter(method=enhanced_type_of_filter)

    class Meta:
        model = ProblemDataSheet
        fields = ['type_of',]


class ProblemDataSheetListAPIView(generics.ListAPIView):
    authentication_classes= (OAuth2Authentication,)
    serializer_class = ProblemDataSheetListSerializer
    # pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanRetrieveUpdateDestroyInvoicePermission
    )
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProblemDataSheetFilter

    def get_queryset(self):
        """
        Get list data.
        """
        queryset = ProblemDataSheet.objects.order_by('type_of', 'text',)
        return queryset
