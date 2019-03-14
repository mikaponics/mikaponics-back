# -*- coding: utf-8 -*-
import re
from datetime import timedelta
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.core.validators import EMPTY_VALUES
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework.response import Response

from foundation.models import User
from foundation import utils


class SendPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        max_length=63,
    )

    def validate(self, clean_data):
        """
        Check to see if the email address is unique and passwords match.
        """
        try:
            clean_data['me'] = User.objects.get(email__iexact=clean_data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Email does not exist.")
        return clean_data
