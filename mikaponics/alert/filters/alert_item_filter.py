# -*- coding: utf-8 -*-
from django_filters import rest_framework as filters

from foundation.models import AlertItem


class AlertItemFilter(filters.FilterSet):
    type_of = filters.NumberFilter(field_name="type_of", )
    state = filters.NumberFilter(field_name="state", )
    production_slug = filters.CharFilter(field_name="production__slug", )
    production_crop_slug = filters.CharFilter(field_name="production_crop__slug", )
    device_slug = filters.CharFilter(field_name="device__slug", )
    instrument_slug = filters.CharFilter(field_name="instrument__slug", )

    o = filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('created_at', 'created_at'),
            ('last_modified_at', 'last_modified_at'),
        ),

        # # labels do not need to retain order
        # field_labels={
        #     'username': 'User account',
        # }
    )

    class Meta:
        model = AlertItem
        fields = [
            'type_of',
            'state',
            'production_slug',
            'production_crop_slug',
            'device_slug',
            'instrument_slug',
        ]
