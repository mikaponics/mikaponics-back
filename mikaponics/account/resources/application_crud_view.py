# -*- coding: utf-8 -*-
import django_filters
from ipware import get_client_ip
from django_filters import rest_framework as filters
from django.conf.urls import url, include
from django.db import transaction
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status,  parsers, renderers
from rest_framework.response import Response

from account.serializers import (
    UserApplicationListCreateSerializer
)
from foundation.models import UserApplication


class UserApplicationListCreateAPIView(generics.ListCreateAPIView):
    # filter_class = UserApplicationFilter
    serializer_class = UserApplicationListCreateSerializer
    # pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanListCreateUserApplicationPermission
    )
    # TODO: https://django-oauth-toolkit.readthedocs.io/en/latest/rest-framework/permissions.html#tokenmatchesoasrequirements

    @transaction.atomic
    def get_queryset(self):
        """
        List
        """
        queryset = UserApplication.objects.filter(user=self.request.user).order_by('-slug')
        return queryset

    @transaction.atomic
    def post(self, request, format=None):
        """
        Create
        """
        serializer = UserApplicationListCreateSerializer(data=request.data, context={
            'authenticated_by': request.user,
            'authenticated_from': request.client_ip,
            'authenticated_from_is_public': request.client_ip_is_routable,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserApplicationRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    # serializer_class = UserApplicationRetrieveUpdateDestroySerializer
    # pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanRetrieveUpdateDestroyUserApplicationPermission
    )
#
#     @transaction.atomic
#     def get(self, request, slug=None):
#         """
#         Retrieve
#         """
#         device = get_object_or_404(UserApplication, slug=slug)
#         self.check_object_permissions(request, device)  # Validate permissions.
#         serializer = UserApplicationRetrieveUpdateDestroySerializer(device, many=False)
#         return Response(
#             data=serializer.data,
#             status=status.HTTP_200_OK
#         )
#
#     @transaction.atomic
#     def put(self, request, slug=None):
#         """
#         Update
#         """
#         device = get_object_or_404(UserApplication, slug=slug)
#         self.check_object_permissions(request, device)  # Validate permissions.
#         client_ip, is_routable = get_client_ip(self.request)
#         serializer = UserApplicationRetrieveUpdateDestroySerializer(device, data=request.data, context={
#             'authenticated_user': request.user,
#             'authenticated_user_from': client_ip,
#             'authenticated_user_from_is_public': is_routable,
#         })
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#
#         # Refresh the recently updated model.
#         device.refresh_from_db()
#
#         # Return our serialized device.
#         s = UserApplicationRetrieveUpdateDestroySerializer(device, many=False, context={
#             'authenticated_user': request.user,
#             'authenticated_user_from': client_ip,
#             'authenticated_user_from_is_public': is_routable,
#         })
#         return Response(
#             data=s.data,
#             status=status.HTTP_200_OK
#         )
#
    @transaction.atomic
    def delete(self, request, slug=None):
        """
        Delete
        """
        application = get_object_or_404(UserApplication, slug=slug)
        self.check_object_permissions(request, application)  # Validate permissions.
        application.delete()
        return Response(data=[], status=status.HTTP_200_OK)



#
# class UserApplicationProfileAPIView(generics.RetrieveUpdateDestroyAPIView):
#     serializer_class = UserApplicationProfileSerializer
#     # pagination_class = StandardResultsSetPagination
#     permission_classes = (
#         # permissions.IsAuthenticated,
#         # IsAuthenticatedAndIsActivePermission,
#         # CanRetrieveUpdateDestroyUserApplicationPermission
#     )
#
#     permission_classes = (
#         permissions.IsAuthenticated,
#         # IsAuthenticatedAndIsActivePermission,
#         # CanListCreateWorkInvoicePermission
#     )
#
#     @transaction.atomic
#     def get(self, request, slug=None):
#         """
#         Retrieve
#         """
#         device = get_object_or_404(UserApplication, slug=slug)
#         self.check_object_permissions(request, device)  # Validate permissions.
#         serializer = UserApplicationProfileSerializer(device, many=False)
#         return Response(
#             data=serializer.data,
#             status=status.HTTP_200_OK
#         )
#
#     @transaction.atomic
#     def put(self, request, slug=None):
#         """
#         Update
#         """
#         device = get_object_or_404(UserApplication, slug=slug)
#         self.check_object_permissions(request, device)  # Validate permissions.
#         serializer = UserApplicationProfileSerializer(device, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)
