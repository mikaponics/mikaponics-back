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

from foundation.models import Device, Instrument, User


class DeviceListCreateSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=User.objects.all(),
        allow_null=False,
    )
    type_of = serializers.IntegerField(required=False, allow_null=True)
    state = serializers.IntegerField(required=False, allow_null=True)
    pretty_state = serializers.ReadOnlyField(source='get_pretty_state')
    created_at = serializers.DateTimeField(read_only=True)
    last_modified_at = serializers.DateTimeField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    absolute_url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = Device
        fields = (
            'uuid',
            'slug',
            'name',
            'description',
            'user',
            'type_of',
            'state',
            'pretty_state',
            'created_at',
            'last_modified_at',
            'is_verified',
            'absolute_url'
        )


class DeviceInstrumentSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True)
    absolute_url = serializers.ReadOnlyField(source='get_absolute_url')
    absolute_parent_url = serializers.ReadOnlyField(source='get_absolute_parent_url')
    unit_of_measure = serializers.ReadOnlyField(source='get_unit_of_measure')
    state = serializers.IntegerField()
    pretty_state = serializers.ReadOnlyField(source='get_pretty_state')
    # last_measured_pretty_value = serializers.ReadOnlyField(source='get_pretty_last_measured_value')
    # last_measured_pretty_at = serializers.ReadOnlyField(source='get_pretty_last_measured_at')
    slug = serializers.SlugField(required=False, allow_blank=True, allow_null=True)
    timezone = serializers.ReadOnlyField(source='device.timezone')
    name = serializers.ReadOnlyField(source='get_pretty_instrument_type_of')
    icon = serializers.ReadOnlyField(source='get_icon')

    class Meta:
        model = Instrument
        fields = (
            'uuid',
            'absolute_url',
            'absolute_parent_url',
            'last_measured_value',
            'last_measured_at',
            'unit_of_measure',
            # 'last_measured_pretty_value',
            # 'last_measured_pretty_at',
            'state',
            'pretty_state',
            'slug',
            'timezone',
            'name',
            'icon',
            'type_of',
        )


class DeviceRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True)
    activated_at = serializers.ReadOnlyField()
    name = serializers.CharField(
        required=True,
        allow_blank=False,
    )
    description = serializers.CharField(
        required=True,
        allow_blank=False,
    )

    slug = serializers.ReadOnlyField()
    absolute_url = serializers.ReadOnlyField(source='get_absolute_url')
    # last_measured_pretty_at = serializers.ReadOnlyField(source='get_pretty_last_measured_at')
    instruments = serializers.SerializerMethodField()
    state = serializers.IntegerField(read_only=True)
    pretty_state = serializers.ReadOnlyField(source='get_pretty_state')
    is_verified = serializers.BooleanField(read_only=True)

    class Meta:
        model = Device
        fields = (
            'uuid',
            'activated_at',
            'timezone',
            'name',
            'description',
            'state',
            'pretty_state',
            'slug',
            'is_verified',
            'absolute_url',
            # 'last_measured_at',
            # 'last_measured_pretty_at',
            'instruments',
        )

    def get_instruments(self, obj):
        try:
            s = DeviceInstrumentSerializer(obj.instruments, many=True)
            return s.data
        except Exception as e:
            print("DeviceRetrieveUpdateDestroySerializer | get_instruments |", e)
        return None

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        # Get our context data.
        authenticated_user = self.context['authenticated_user']
        authenticated_user_from = self.context['authenticated_user_from']
        authenticated_user_from_is_public = self.context['authenticated_user_from_is_public']

        # Save our inputted & context data.
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.last_modified_by = authenticated_user
        instance.last_modified_from = authenticated_user_from
        instance.last_modified_from_is_public = authenticated_user_from_is_public
        instance.save()

        # instance.invoice.invalidate('total')
        return validated_data

    def delete(self, instance):
        instance.delete()



class DeviceProfileSerializer(serializers.ModelSerializer):

    name = serializers.CharField(
        required=True,
        allow_blank=False,
    )
    description = serializers.CharField(
        required=True,
        allow_blank=False,
    )

    class Meta:
        model = Device
        fields = (
            'name',
            'description',
        )
