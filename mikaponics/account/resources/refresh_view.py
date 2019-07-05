# -*- coding: utf-8 -*-
import django_filters
from oauthlib.common import generate_token
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
from foundation.drf.permissions import DisableOptionsPermission


class RefreshTokenAPIView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes= (OAuth2Authentication,)
    permission_classes = (
        DisableOptionsPermission,
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
    def post(self, request):
        # STEP 1:
        # Lookup the refresh token and if it does not exist then return 401 error.
        token = request.data.get('refresh_token', None)
        refresh_token = RefreshToken.objects.filter(token=token).first()
        if refresh_token is None:
            print(token, "not found!")
            return Response(data=[], status=status.HTTP_401_UNAUTHORIZED)

        # STEP 2:
        # Make the refresh token and access token not longer valid.
        refresh_token.revoked = timezone.now()
        refresh_token.save()
        refresh_token.access_token.expires = timezone.now()
        refresh_token.access_token.save()

        # STEP 3:
        # Create our new access token and refresh token....
        # Get our web application authorization.
        application = Application.objects.filter(name=settings.MIKAPONICS_RESOURCE_SERVER_NAME).first()

        # Generate our "NEW" access token which does not have a time limit.
        # We want to generate a new token every time because the user may be
        # logging in from multiple locations and may log out from multiple
        # locations so we don't want the user using the same token every time.
        aware_dt = timezone.now()
        expires_dt = aware_dt + timezone.timedelta(days=1)
        access_token = AccessToken.objects.create(
            application=application,
            user=refresh_token.user,
            expires=expires_dt,
            token=generate_token(),
            scope='read,write,introspection'
        )

        refresh_token = RefreshToken.objects.create(
            application = application,
            user = refresh_token.user,
            access_token=access_token,
            token=generate_token()
        )

        # STEP 4:
        # Return our new credentials.
        revoked_at = int(refresh_token.revoked.timestamp()) if refresh_token.revoked is not None else None
        return Response(data={
            'access_token': {
                'token': str(access_token),
                'expires': int(access_token.expires.timestamp()),
                'scope': str(access_token.scope)
            },
            'refresh_token': {
                'token': str(refresh_token),
                'revoked': revoked_at,
            }
        }, status=status.HTTP_200_OK)
