# -*- coding: utf-8 -*-
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework.response import Response

from foundation.models import User


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, allow_blank=False)
    password = serializers.CharField(required=True, allow_blank=False)
    password_repeat = serializers.CharField(required=True, allow_blank=False)
    first_name = serializers.CharField(required=True, allow_blank=False)
    last_name = serializers.CharField(required=True, allow_blank=False)
    timezone = serializers.CharField(required=True, allow_blank=False)

    def validate(self, attrs):
        email = attrs.get('email', None)
        password = attrs.get('password', None)
        password_repeat = attrs.get('password_repeat', None)
        first_name = attrs.get('first_name', None)
        last_name = attrs.get('last_name', None)
        timezone = attrs.get('timezone', None)

        # Defensive Code: Prevent continuing if the email already exists.
        if User.objects.filter(email=email).exists():
            raise exceptions.ValidationError(_('Email already exists, please pick another email.'))

        # Confirm passwords match.
        if password != password_repeat:
            raise exceptions.ValidationError(_('Passwords do not match.'))

        # Return our validated data.
        return attrs

    def create(self, validated_data):
        email = validated_data.get('email', None)
        password = validated_data.get('password', None)
        first_name = validated_data.get('first_name', None)
        last_name = validated_data.get('last_name', None)
        timezone = attrs.get('timezone', None)

        # Create the user.
        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_active=True,
            is_superuser=False,
            is_staff=False,
            was_email_activated=False, # User email must be activated before usage.
            timezone=timezone,
        )

        # Generate and assign the password.
        user.set_password(password)
        user.save()

        # Refresh our object.
        user.refresh_from_db()

        # Update our validated data.
        validated_data['client_id'] = user.id
        validated_data['user'] = user

        # Return our output
        return validated_data
