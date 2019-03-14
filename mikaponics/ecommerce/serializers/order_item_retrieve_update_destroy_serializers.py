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

from ecommerce.models import Order, Product


logger = logging.getLogger(__name__)


def get_todays_date_plus_days(days=0):
    """Returns the current date plus paramter number of days."""
    return timezone.now() + timedelta(days=days)


class OrderItemRetrieveUpdateDestroySerializer(serializers.Serializer):
    order = serializers.PrimaryKeyRelatedField(read_only=True)
    product = serializers.PrimaryKeyRelatedField(read_only=True)
    number_of_products = serializers.IntegerField(required=False, allow_null=True)

    # Meta Information.
    class Meta:
        fields = (
            'order',
            'product',
            'number_of_products'
        )

    def validate_number_of_products(self, data):
        if data < 1:
            raise exceptions.ValidationError(_("Please pick number greater then zero."))
        return data

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        instance.number_of_products = validated_data.get('number_of_products', instance.number_of_products)
        instance.save()
        instance.order.invalidate('total')
        return validated_data

    def delete(self, instance):
        instance.delete()
