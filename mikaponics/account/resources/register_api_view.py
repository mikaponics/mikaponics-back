# -*- coding: utf-8 -*-
import django_rq
import logging
from datetime import datetime
from ipware import get_client_ip
from django.conf import settings
from django.conf.urls import url, include
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from django.db import connection # Used for django tenants.
from django.http import Http404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from oauthlib.common import generate_token
from oauth2_provider.models import Application, AbstractApplication, AbstractAccessToken, AccessToken, RefreshToken
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import mixins # See: http://www.django-rest-framework.org/api-guide/generic-views/#mixins
from rest_framework import authentication, viewsets, permissions, status, parsers, renderers
from rest_framework.decorators import detail_route, list_route # See: http://www.django-rest-framework.org/api-guide/viewsets/#marking-extra-actions-for-routing
from rest_framework.response import Response

from account.serializers import RegisterSerializer
from account.tasks import run_send_activation_email_func, run_send_user_was_created_to_staff_email_func


class RegisterAPIView(APIView):
    """
    API endpoint used for users to input their email and password to get the
    oAuth 2.0 token which can be used in remote resource servers.
    """
    throttle_classes = ()
    permission_classes = ()

    def post(self, request):
        # Get the IP of the user.
        client_ip, is_routable = get_client_ip(self.request)

        # Save our code and return the serialized data.
        serializer = RegisterSerializer(data=request.data, context={
            'request': request,
        })
        serializer.is_valid(raise_exception=True)
        data = serializer.save()

        # Get the newly created user from the registration.
        authenticated_user = data['user']

        # Send our activation email to the user.
        django_rq.enqueue(run_send_activation_email_func, email=authenticated_user.email)
        django_rq.enqueue(run_send_user_was_created_to_staff_email_func, email=authenticated_user.email)

        # Return a simple message indicating that the user was registered.
        return Response(data={}, status=status.HTTP_201_CREATED)
