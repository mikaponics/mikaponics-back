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

from ecommerce.serializers import StripeEventSerializer


class StripeEventAPIView(APIView):
    """
    """
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (
        parsers.FormParser,
        parsers.MultiPartParser,
        parsers.JSONParser,
    )

    renderer_classes = (renderers.JSONRenderer,)

    def post(self, request):
        # Defensive Code: Make sure that Stripe sent the request before we
        #                 do any processing.
        if "HTTP_STRIPE_SIGNATURE" not in request.META:
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

        # Get the IP.
        client_ip, is_routable = get_client_ip(self.request)

        # Serialize our input.
        serializer = StripeEventSerializer(data=request.data, context={
            'from': client_ip,
            'from_is_public': is_routable,
        })

        # Validate and save.
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return our new token.
        return Response(serializer.data, status=status.HTTP_201_CREATED)
