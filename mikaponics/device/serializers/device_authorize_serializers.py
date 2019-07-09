# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response

from foundation.models import Device, Instrument, User
from foundation.constants import MIKAPONICS_AUTHORIZED_DEVICE_PRODUCT_ID


class DeviceAuthorizeSerializer(serializers.ModelSerializer):

    name = serializers.CharField(
        required=True,
        allow_blank=False,
    )
    description = serializers.CharField(
        required=True,
        allow_blank=False,
    )
    instruments = serializers.JSONField(
        required=True,
        allow_null=False,
    )

    class Meta:
        model = Device
        fields = (
            'name',
            'description',
            'instruments',
        )

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        # Get our context data.
        authenticated_user = self.context['authenticated_user']
        authenticated_user_from = self.context['authenticated_user_from']
        authenticated_user_from_is_public = self.context['authenticated_user_from_is_public']

        # Get user input.
        name = validated_data.get('name')
        description = validated_data.get('description')
        instruments = validated_data.get('instruments')

        # Create our device.
        device = Device.objects.create(
            is_verified=False,
            product_id=MIKAPONICS_AUTHORIZED_DEVICE_PRODUCT_ID,
            name=name,
            description=description,
            user=authenticated_user,
            created_by=authenticated_user,
            created_from=authenticated_user_from,
            created_from_is_public=authenticated_user_from_is_public,
            last_modified_by=authenticated_user,
            last_modified_from=authenticated_user_from,
            last_modified_from_is_public=authenticated_user_from_is_public
        )

        # Create our instruments and update our values.
        instruments_with_uuids = []
        for data in instruments:
            type_of = data.get('type_of')
            if type_of is None:
                type_of = data.get('value')

            instrument = Instrument.objects.create(
                device=device,
                type_of=type_of,
                time_step=Instrument.TIME_STEP.EVERY_MINUTE
            )
            data['uuid'] = str(instrument.uuid)
            instruments_with_uuids.append(data)

        # Set our additional extra values and return all our validated values.
        validated_data["instruments"] = instruments_with_uuids
        validated_data['uuid'] = str(device.uuid)
        return validated_data
