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

from foundation.models import CropDataSheet


class CropDataSheetListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CropDataSheet
        fields = (
            'name',
            'type_of',
            'slug',
        )
