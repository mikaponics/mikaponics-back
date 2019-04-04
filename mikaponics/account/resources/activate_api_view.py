# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from ipware import get_client_ip
from django.conf.urls import url, include
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from django.db import connection # Used for django tenants.
from django.http import Http404
from django.utils import timezone
from oauthlib.common import generate_token
from oauth2_provider.models import Application, AbstractApplication, AbstractAccessToken, AccessToken, RefreshToken
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import mixins # See: http://www.django-rest-framework.org/api-guide/generic-views/#mixins
from rest_framework import authentication, viewsets, permissions, status, parsers, renderers
from rest_framework.decorators import detail_route, list_route # See: http://www.django-rest-framework.org/api-guide/viewsets/#marking-extra-actions-for-routing
from rest_framework.response import Response

from account.serializers import ActivateSerializer, ProfileInfoRetrieveUpdateSerializer


class ActivateAPIView(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (
        parsers.FormParser,
        parsers.MultiPartParser,
        parsers.JSONParser,
    )

    renderer_classes = (renderers.JSONRenderer,)

    def post(self, request):
        # Get the IP of the user.
        client_ip, is_routable = get_client_ip(self.request)

        # Serializer to get our login details.
        serializer = ActivateSerializer(data=request.data, context={
            'request': request,
        })
        serializer.is_valid(raise_exception=True)
        authenticated_user = serializer.save()
        authenticated_user.refresh_from_db()

        # Get our web application authorization.
        application = Application.objects.filter(name=settings.MIKAPONICS_RESOURCE_SERVER_NAME).first()

        # Generate our access token which does not have a time limit.
        aware_dt = timezone.now()
        expires_dt = aware_dt.replace(aware_dt.year + 1776)
        access_token, created = AccessToken.objects.update_or_create(
            application=application,
            user=authenticated_user,
            defaults={
                'user': authenticated_user,
                'application': application,
                'expires': expires_dt,
                'token': generate_token(),
                'scope': 'read,write,introspection'
            },
            scope='read,write,introspection'
        )

        serializer = ProfileInfoRetrieveUpdateSerializer(authenticated_user, many=False, context={
            'authenticated_by': authenticated_user,
            'authenticated_from': client_ip,
            'authenticated_from_is_public': is_routable,
            'token': str(access_token),
            'scope': access_token.scope,
        })
        return Response(serializer.data, status=status.HTTP_200_OK)
