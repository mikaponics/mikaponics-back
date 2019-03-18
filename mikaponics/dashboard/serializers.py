# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db.models import Q, Prefetch, Sum
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator

from foundation.models import Order, Product


logger = logging.getLogger(__name__)


class DashboardSerializer(serializers.Serializer):
    # --- Authentication Credentials ---
    token = serializers.SerializerMethodField()

    # Meta Information.
    class Meta:
        fields = (
            # --- Authentication Credentials ---
            'token',
        )

    def get_token(self, obj):
        print(">>>")
        return self.context.get('token', None)
