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


class TaskItemListSerializer(serializers.ModelSerializer):
    pretty_type_of = serializers.CharField(read_only=True, source="get_pretty_type_of")
    absolute_url = serializers.CharField(read_only=True, source="get_absolute_url")

    class Meta:
        model = TaskItem
        fields = (
            'pretty_type_of',
            'type_of',
            'slug',
            'due_date',
            'created_at',
            'is_closed',
            'absolute_url',
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            # 'instrument',
            # 'instrument__device',
        )
        return queryset
