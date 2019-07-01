# -*- coding: utf-8 -*-
from ipware import get_client_ip
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasScope
from django.db import transaction
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status,  parsers, renderers
from rest_framework.response import Response

from foundation.models import Invoice


class InvoiceCalculationFuncView(generics.CreateAPIView):
    authentication_classes= (OAuth2Authentication,)
    permission_classes = (
        permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanListCreateWorkInvoicePermission
    )

    @transaction.atomic
    def put(self, request, pk=None):
        """
        Create
        """
        obj = Invoice.objects.select_for_update().filter(pk=pk).first()
        if obj is None:
            raise Http404()

        # Perform our calculation or fetch our pre-computed total (assuming no
        # update was made).
        results = obj.total()

        # For debuggin purposes only.
        print(results)

        # Return our calculation result
        return Response(results, status=status.HTTP_200_OK)
