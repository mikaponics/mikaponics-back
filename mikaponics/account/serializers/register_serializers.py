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

from foundation.models import User
from foundation.model_resources import grant_referral_program_coupons


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, allow_blank=False)
    password = serializers.CharField(required=True, allow_blank=False)
    password_repeat = serializers.CharField(required=True, allow_blank=False)
    first_name = serializers.CharField(required=True, allow_blank=False)
    last_name = serializers.CharField(required=True, allow_blank=False)
    timezone = serializers.CharField(required=True, allow_blank=False)
    has_signed_tos = serializers.BooleanField(required=True)
    referral_code = serializers.CharField(required=False, allow_blank=True, allow_null=True,)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise exceptions.ValidationError(_('Email already exists, pick another email.'))
        return value

    def validate_has_signed_tos(self, value):
        if value is False or value == False:
            raise exceptions.ValidationError(_('Please sign the terms of service before submitting.'))
        return value

    def validate_referral_code(self, value):
        # CASE 1 OF 2: Empty value
        if value == None or value == 'None' or value == 'null' or value == '':
            return None

        # CASE 2 OF 2: Non-Empty Value
        if User.objects.filter(referral_code=value).exists():
            return value
        else:
            raise exceptions.ValidationError(_('Please enter a correct referral code.'))

    def validate(self, attrs):
        email = attrs.get('email', None)
        password = attrs.get('password', None)
        password_repeat = attrs.get('password_repeat', None)
        first_name = attrs.get('first_name', None)
        last_name = attrs.get('last_name', None)
        timezone_name = attrs.get('timezone', None)

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
        timezone_name = validated_data.get('timezone', None)
        has_signed_tos = validated_data.get('has_signed_tos', False)
        referral_code = validated_data.get('referral_code', None)

        # Open up the current "terms of agreement" file and extract the text
        # context which we will save with the user account.
        tos_agreement = render_to_string('account/terms_of_service/2019_05_01.txt', {})

        # Attempt to lookup the referee of this user.
        referred_by_user = User.objects.filter(referral_code=referral_code).first()

        # Create the user.
        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_active=True,
            is_superuser=False,
            is_staff=False,
            was_email_activated=False, # User email must be activated before usage.
            timezone=timezone_name,
            billing_given_name = first_name,
            billing_last_name = last_name,
            billing_email = email,
            shipping_given_name = first_name,
            shipping_last_name = last_name,
            shipping_email = email,
            has_signed_tos = has_signed_tos,
            tos_agreement = tos_agreement,
            tos_signed_on = timezone.now(),
            referred_by = referred_by_user,
        )

        # Generate and assign the password.
        user.set_password(password)
        user.save()

        # Refresh our object.
        user.refresh_from_db()

        # The following code will generate the two (one-time usage) coupons to
        # the referee (the new user in the system) and the referrer (the user
        # whom referred this newly registered user).
        if referral_code:
            grant_referral_program_coupons(
                referrer=referred_by_user,
                referee=user
            )

        # Update our validated data.
        validated_data['client_id'] = user.id
        validated_data['user'] = user

        # Return our output
        return validated_data
