# -*- coding: utf-8 -*-
import django_filters
from ipware import get_client_ip
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasScope
from django.conf import settings
from django.db import transaction
from django.http import Http404
from django_filters import rest_framework as filters
from django.conf.urls import url, include
from django.utils import timezone
from oauth2_provider.models import Application, AbstractApplication, AbstractAccessToken, AccessToken, RefreshToken
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status,  parsers, renderers
from rest_framework.response import Response

from account.serializers import ProfileInfoRetrieveUpdateSerializer


class ProfileInfoRetrieveUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes= (OAuth2Authentication,)
    serializer_class = ProfileInfoRetrieveUpdateSerializer
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
        return self.request.user

    @transaction.atomic
    def get(self, request):
        """
        Retrieve
        """
        client_ip, is_routable = get_client_ip(self.request)
        self.check_object_permissions(request, request.user)  # Validate permissions.

        # Fetch our application and token for the user.
        application = Application.objects.filter(name=settings.MIKAPONICS_RESOURCE_SERVER_NAME).first()
        access_token = AccessToken.objects.filter(user=request.user, application=application).order_by('-created').first()

        serializer = ProfileInfoRetrieveUpdateSerializer(request.user, context={
            'authenticated_by': request.user,
            'authenticated_from': client_ip,
            'authenticated_from_is_public': is_routable,
            'token': str(access_token),
            'scope': 'read,write,introspection'
        })
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request):
        """
        Update
        """
        client_ip, is_routable = get_client_ip(self.request)
        self.check_object_permissions(request, request.user)  # Validate permissions.

        # Fetch our application and token for the user.
        application = Application.objects.filter(name=settings.MIKAPONICS_RESOURCE_SERVER_NAME).first()
        access_token = AccessToken.objects.filter(user=request.user, application=application).order_by('-created').first()

        serializer = ProfileInfoRetrieveUpdateSerializer(request.user, data=request.data, context={
            'authenticated_by': request.user,
            'authenticated_from': client_ip,
            'authenticated_from_is_public': is_routable,
            'token': str(access_token),
            'scope': 'read,write,introspection'
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
