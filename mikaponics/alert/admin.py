from ipware import get_client_ip
from prettyjson import PrettyJSONWidget
from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
# from django.contrib.auth.admin import UserAdmin

from foundation.models import *


class AlertItemAdmin(admin.ModelAdmin):
    raw_id_fields = [
        'user', 'device', 'instrument', 'production', 'production_crop'
    ]
    list_filter = [
        'type_of', 'condition', 'state',
    ]
    list_display = [
        'slug', 'type_of', 'user', 'condition', 'state',
    ]
    ordering = ['-id',]
    readonly_fields = [
        'created_at', 'id', 'slug'
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
