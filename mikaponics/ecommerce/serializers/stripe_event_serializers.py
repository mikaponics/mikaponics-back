# -*- coding: utf-8 -*-
import django_rq
import logging
import pytz
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

from foundation.models import StripeEvent
from ecommerce.tasks import run_process_stripe_event_by_id_func


logger = logging.getLogger(__name__)


def get_todays_date_plus_days(days=0):
    """Returns the current date plus paramter number of days."""
    return timezone.now() + timedelta(days=days)


class StripeEventSerializer(serializers.Serializer):
    created = serializers.IntegerField(required=True)
    livemode = serializers.BooleanField(required=True)
    id = serializers.CharField(required=True)
    type = serializers.CharField(required=True)
    object = serializers.CharField(required=True)
    request = serializers.JSONField(required=False, allow_null=True)
    pending_webhooks = serializers.IntegerField(required=True)
    api_version = serializers.CharField(required=True)
    data = serializers.JSONField(required=True)

    # Meta Information.
    class Meta:
        fields = (
            'created',
            'livemode',
            'id',
            'type',
            'object',
            'request',
            'pending_webhooks',
            'api_version',
            'data',
        )

    def create(self, validated_data):
        """
        Override this function to include extra functionality.
        """
        from_ip = self.context.get('from')
        from_ip_is_public = self.context.get('from_is_public')
        created_ts = validated_data.get('created')
        livemode = validated_data.get('livemode')
        id = validated_data.get('id')
        type = validated_data.get('type')
        object = validated_data.get('object')
        request = validated_data.get('request', None)
        pending_webhooks = validated_data.get('pending_webhooks')
        api_version = validated_data.get('api_version')
        data = validated_data.get('data')

        # Process datatime.
        naive_dt = datetime.fromtimestamp(created_ts)
        utc_aware_dt = naive_dt.replace(tzinfo=pytz.utc)

        event_id = StripeEvent.objects.create(
            created=utc_aware_dt,
            livemode=livemode,
            event_id=id,
            type=type,
            object=object,
            request=request,
            pending_webhooks=pending_webhooks,
            api_version=api_version,
            data=data,
            created_from=from_ip,
            created_from_is_public=from_ip_is_public,
        )

        # Send our activation email to the user.
        django_rq.enqueue(run_process_stripe_event_by_id_func, event_id.id)

        # Return our validated dated.
        return validated_data
