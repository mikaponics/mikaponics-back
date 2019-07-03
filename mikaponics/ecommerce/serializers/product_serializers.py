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

from foundation.models import Product


logger = logging.getLogger(__name__)


def get_todays_date_plus_days(days=0):
    """Returns the current date plus paramter number of days."""
    return timezone.now() + timedelta(days=days)


class ProductListSerializer(serializers.ModelSerializer):
    state = serializers.IntegerField(read_only=True)
    slug = serializers.SlugField(read_only=True)
    sort_number = serializers.IntegerField(read_only=True)
    icon = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    short_description = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    price = serializers.FloatField(read_only=True)
    pretty_price = serializers.SerializerMethodField()

    # Meta Information.
    class Meta:
        model = Product
        fields = (
            'state',
            'slug',
            'sort_number',
            'icon',
            'name',
            'short_description',
            'description',
            'price',
            'pretty_price',
        )

    def get_pretty_price(self, obj):
        return str(obj.price)
