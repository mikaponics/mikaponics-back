from ipware import get_client_ip
from prettyjson import PrettyJSONWidget
from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
# from django.contrib.auth.admin import UserAdmin

from foundation.models import *


class TimeSeriesImageDatumAdmin(admin.ModelAdmin):
    """
    Read-only class GUI to prevent the administrators from adding data that
    was not created by the instrument. This is done to protect the administrator
    from themeselves.
    """
    list_display = ['id', 'instrument_id', 'timestamp',]
    ordering = ['-id',]
    raw_id_fields = ['instrument',]
    readonly_fields = [
        # 'instrument', 'value', 'timestamp'
        'next', 'previous', 'created_from', 'created_from_is_public',
    ]

    # def has_add_permission(self, request, obj=None):
    #     return False
    #
    # def has_delete_permission(self, request, obj=None):
    #     return False

admin.site.register(TimeSeriesImageDatum, TimeSeriesImageDatumAdmin)


class TimeSeriesDatumAdmin(admin.ModelAdmin):
    """
    Read-only class GUI to prevent the administrators from adding data that
    was not created by the instrument. This is done to protect the administrator
    from themeselves.
    """
    list_display = ['id', 'instrument_id', 'value', 'timestamp',]
    ordering = ['-id',]
    raw_id_fields = ['instrument',]
    readonly_fields = [
        # 'instrument', 'value', 'timestamp'
        'next', 'previous', 'created_from', 'created_from_is_public',
    ]

    # def has_add_permission(self, request, obj=None):
    #     return False
    #
    # def has_delete_permission(self, request, obj=None):
    #     return False

admin.site.register(TimeSeriesDatum, TimeSeriesDatumAdmin)
