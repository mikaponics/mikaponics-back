# -*- coding: utf-8 -*-
from django_filters import rest_framework as filters

from foundation.models import ProductionInspection


class ProductionInspectionFilter(filters.FilterSet):
    production_slug = filters.CharFilter(field_name="production__slug", )
    state = filters.NumberFilter(field_name="state", )

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
        model = ProductionInspection
        fields = [
            'production_slug',
            'state',
        ]
