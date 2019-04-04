# -*- coding: utf-8 -*-
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework.response import Response

from foundation.models import User


class ActivateSerializer(serializers.Serializer):
    pr_access_code = serializers.CharField(required=True, allow_blank=False)

    def create(self, validated_data):
        pr_access_code = validated_data.get('pr_access_code', None)

        try:
            user = User.objects.filter(pr_access_code=pr_access_code).first()
            if user is None:
                raise exceptions.ValidationError(_('Access token is invalid.'))

            if user.has_pr_code_expired():
                raise exceptions.ValidationError(_('Access token has expired.'))

            # Save the state.
            user.was_email_activated = True
            user.save()
        except User.DoesNotExist:
            raise exceptions.ValidationError(_('Invalid credentials provided.'))

        # Save the validation.
        return user
