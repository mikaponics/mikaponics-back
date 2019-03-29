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

from foundation.models import Invoice, Product


logger = logging.getLogger(__name__)


def get_todays_date_plus_days(days=0):
    """Returns the current date plus paramter number of days."""
    return timezone.now() + timedelta(days=days)


class InvoiceListCreateSerializer(serializers.Serializer):
    state = serializers.CharField(read_only=True, source="get_pretty_state")
    grand_total = serializers.CharField(read_only=True)
    slug = serializers.SlugField(read_only=True)
    absolute_url = serializers.ReadOnlyField(source="get_absolute_url")
    purchased_at = serializers.DateTimeField(read_only=True)

    # Meta Information.
    class Meta:
        fields = (
            'state',
            'grand_total',
            'slug',
            'absolute_url',
            'purchased_at',
        )
