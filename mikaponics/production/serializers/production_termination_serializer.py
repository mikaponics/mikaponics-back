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

from foundation.models import Crop, Production
from production.serializers.production_crop_list_serializer import ProductionCropListSerializer


class ProductionTerminationSerializer(serializers.ModelSerializer):

    plants = serializers.JSONField(required=True, allow_null=True,)
    fish = serializers.JSONField(required=True, allow_null=True,)

    class Meta:
        model = Production
        fields = (
            'plants',
            'fish',
        )

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        # Get our context data.
        authenticated_user = self.context['authenticated_by']
        authenticated_user_from = self.context['authenticated_from']
        authenticated_user_from_is_public = self.context['authenticated_from_is_public']

        # Get our inputted data.
        plants = validated_data.get('plants', None)
        fish = validated_data.get('fish', None)

        #TODO: IMPLEMENT...

        # instance.invoice.invalidate('total')
        return validated_data
