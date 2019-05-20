from ipware import get_client_ip
from prettyjson import PrettyJSONWidget
from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
# from django.contrib.auth.admin import UserAdmin

from foundation.models import *


class AlertItemAdmin(admin.ModelAdmin):
    raw_id_fields = ['user', 'device', 'instrument', 'production', 'production_crop']
    list_filter = ['condition', 'state',]
    list_display = ['slug', 'id', 'user', 'condition', 'state',]
    ordering = ['-id',]
    readonly_fields = [
        # 'created_at', 'created_by', 'created_from',
        # 'created_from_is_public', 'last_modified_at', 'last_modified_by',
        # 'last_modified_from', 'last_modified_from_is_public', 'activated_at',
        # 'last_measured_value', 'last_measured_at',
        # 'last_measured_unit_of_measure', 'get_environment_variables_file_url',
    ]
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget }
    }

    # def save_model(self, request, obj, form, change):
    #     """
    #     Override the `save` function in `Django Admin` to include audit details
    #     and the following additions:
    #     (1) Create our API token which the device will be using for making API
    #         calls to our service.
    #     """
    #     client_ip, is_routable = get_client_ip(request)
    #     obj.created_by = request.user
    #     obj.created_from = client_ip
    #     obj.created_from_is_public = is_routable
    #     obj.last_modified_by = request.user
    #     obj.last_modified_from = client_ip
    #     obj.last_modified_from_is_public = is_routable
    #     super().save_model(request, obj, form, change)


admin.site.register(AlertItem, AlertItemAdmin)
