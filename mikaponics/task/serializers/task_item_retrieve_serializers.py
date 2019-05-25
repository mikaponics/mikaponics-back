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

from foundation.models import TaskItem


class TaskItemRetrieveSerializer(serializers.ModelSerializer):
    pretty_type_of = serializers.CharField(read_only=True, source="get_pretty_type_of")
    absolute_url = serializers.CharField(read_only=True, source="get_absolute_url")
    production_inspection_slug = serializers.CharField(read_only=True, source="production_inspection.slug", allow_null=False)

    class Meta:
        model = TaskItem
        fields = (
            'pretty_type_of',
            'type_of',
            'slug',
            'title',
            'description',
            'due_date',
            'created_at',
            'last_modified_at',
            'is_closed',
            'production_inspection_slug',
            'link',
            'is_external_link',
            'absolute_url',
        )

    # def get_state(self, obj):
    #     return obj.get_pretty_state()
