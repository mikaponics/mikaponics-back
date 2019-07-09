# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response

from foundation.models import UserApplication


class UserApplicationListCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True, allow_blank=False, allow_null=False,)
    description = serializers.CharField(required=True, allow_blank=False, allow_null=False,)
    slug = serializers.SlugField(read_only=True,)

    class Meta:
        model = UserApplication
        fields = (
            'name',
            'description',
            'slug',
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'user',
        )
        return queryset

    def create(self, validated_data):
        # Get inputs.
        user = self.context.get('authenticated_by')
        ip = self.context.get('authenticated_from')
        ip_is_routable = self.context.get('authenticated_from_is_public')
        name = validated_data.get('name', None)
        description = validated_data.get('description', None)

        # Save our objects.
        instance = UserApplication.objects.create(
            user=user,
            name=name,
            description=description,
            created_by=user,
            created_from=ip,
            created_from_is_public=ip_is_routable,
            last_modified_by=user,
            last_modified_from=ip,
            last_modified_from_is_public=ip_is_routable,
        )

        # Save our outputs and return them.
        validated_data['slug'] = instance.slug
        return validated_data
