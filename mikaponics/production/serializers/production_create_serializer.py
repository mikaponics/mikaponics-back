# -*- coding: utf-8 -*-
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string  # HTML / TXT
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework.response import Response

from foundation.models import Production


class ProductionCreateSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    description = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    device_slug = serializers.SlugField(required=True, allow_blank=False, allow_null=False)
    # password_repeat = serializers.CharField(required=True, allow_blank=False)
    # first_name = serializers.CharField(required=True, allow_blank=False)
    # last_name = serializers.CharField(required=True, allow_blank=False)
    # timezone = serializers.CharField(required=True, allow_blank=False)
    # has_signed_tos = serializers.BooleanField(required=True)
    # referral_code = serializers.CharField(required=False, allow_blank=True, allow_null=True,)

    class Meta:
        model = Production
        fields = (
            'name',
            'description',
            # 'state',
            # 'previous',
            # 'device',
            # 'environment',
            # 'is_commercial',
            # 'type_of',
            # 'grow_system',
            # 'grow_system_other',
            # 'started_at',
        )

    # def validate_email(self, value):
    #     if User.objects.filter(email=value).exists():
    #         raise exceptions.ValidationError(_('Email already exists, pick another email.'))
    #     return value
    #
    # def validate_has_signed_tos(self, value):
    #     if value is False or value == False:
    #         raise exceptions.ValidationError(_('Please sign the terms of service before submitting.'))
    #     return value
    #
    # def validate_referral_code(self, value):
    #     if User.objects.filter(referral_code=value).exists():
    #         return value
    #     else:
    #         raise exceptions.ValidationError(_('Please enter a correct referral code.'))
    #
    # def validate(self, attrs):
    #     email = attrs.get('email', None)
    #     password = attrs.get('password', None)
    #     password_repeat = attrs.get('password_repeat', None)
    #     first_name = attrs.get('first_name', None)
    #     last_name = attrs.get('last_name', None)
    #     timezone_name = attrs.get('timezone', None)
    #
    #     # Defensive Code: Prevent continuing if the email already exists.
    #     if User.objects.filter(email=email).exists():
    #         raise exceptions.ValidationError(_('Email already exists, please pick another email.'))
    #
    #     # Confirm passwords match.
    #     if password != password_repeat:
    #         raise exceptions.ValidationError(_('Passwords do not match.'))
    #
    #     # Return our validated data.
    #     return attrs

    def create(self, validated_data):
        # Get our validated data and context data.
        name = validated_data.get('name', None)
        description = validated_data.get('description', None)
        device_slug = validated_data.get('device_slug', None)
        user = self.context['authenticated_by']

        Production.objects.create(
            name=name,
            description=description,
            user=user,
        )

        # Return our output
        return validated_data
