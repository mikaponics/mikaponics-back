from ipware import get_client_ip
from prettyjson import PrettyJSONWidget
from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
# from django.contrib.auth.admin import UserAdmin

from foundation.models import *


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    raw_id_fields = ['referred_by',]
    list_display = ['email', 'is_staff', 'is_active', 'was_email_activated', 'was_onboarded', 'referred_by',]
    list_filter = ('is_staff',  'is_active', 'was_email_activated', 'was_onboarded', )

    fieldsets = (
        (None,
            {'fields': ('email','password')}
        ),

        ('Global Settings',
            {'fields': ('timezone',)}
        ),

        ('Permissions',
            {'fields': ('is_staff',)}
        ),

        ('Billing Information',
            {'fields': ('billing_given_name', 'billing_last_name', 'billing_email')}
        ),

        ('Shipping Information',
            {'fields': ('shipping_given_name', 'shipping_last_name', 'shipping_email')}
        ),

        ('E-Ecommerce',
            {'fields':
                (
                'was_onboarded', 'customer_id','customer_data', 'subscription_id',
                'subscription_status', 'subscription_start_date', 'subscription_data',
                'referral_code', 'referred_by',
                )
            }
        ),

        ('Email Activation / Password Reset',
            {'fields': ('was_email_activated', 'pr_access_code', 'pr_expiry_date')}
        ),

        ('Terms of Service',
            {'fields': ('has_signed_tos', 'tos_agreement', 'tos_signed_on')}
        ),
    )
    readonly_fields = ['subscription_status',]

    search_fields =  ['email',]
    ordering = ['email',]

    filter_horizontal = ()

admin.site.register(User, UserAdmin)
admin.site.unregister(Group)


class InstrumentInline(admin.TabularInline):
    model = Instrument


class DeviceAdmin(admin.ModelAdmin):
    inlines = [
        InstrumentInline,
    ]
    raw_id_fields = ['user', 'invoice',]
    list_filter = ['product', 'state',]
    list_display = ['slug', 'id', 'name', 'user', 'product', 'state',]
    ordering = ['-id',]
    readonly_fields = [
        'uuid', 'created_at', 'created_by', 'created_from',
        'created_from_is_public', 'last_modified_at', 'last_modified_by',
        'last_modified_from', 'last_modified_from_is_public', 'activated_at',
        'last_measurement', 'last_camera_snapshot',
        'get_environment_variables_file_url',
    ]
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget }
    }

    def save_model(self, request, obj, form, change):
        """
        Override the `save` function in `Django Admin` to include audit details
        and the following additions:
        (1) Create our API token which the device will be using for making API
            calls to our service.
        """
        client_ip, is_routable = get_client_ip(request)
        obj.created_by = request.user
        obj.created_from = client_ip
        obj.created_from_is_public = is_routable
        obj.last_modified_by = request.user
        obj.last_modified_from = client_ip
        obj.last_modified_from_is_public = is_routable
        super().save_model(request, obj, form, change)


admin.site.register(Device, DeviceAdmin)


class InstrumentAdmin(admin.ModelAdmin):
    list_display = ['slug', 'id', 'device_id', 'type_of', 'last_modified_at']
    list_filter = ['type_of',]
    # search_fields = ['device_id',]
    raw_id_fields = ['device',]
    ordering = ['-id',]
    readonly_fields = [
        'id', 'uuid', 'created_at', 'created_by', 'created_from',
        'created_from_is_public', 'last_modified_at', 'last_modified_by',
        'last_modified_from', 'last_modified_from_is_public',
        'last_measured_value', 'last_measured_at',
    ]
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget }
    }

    def save_model(self, request, obj, form, change):
        """
        Override the `save` function in `Django Admin` to include audit details.
        """
        client_ip, is_routable = get_client_ip(request)
        obj.created_by = request.user
        obj.created_from = client_ip
        obj.created_from_is_public = is_routable
        obj.last_modified_by = request.user
        obj.last_modified_from = client_ip
        obj.last_modified_from_is_public = is_routable
        super().save_model(request, obj, form, change)

admin.site.register(Instrument, InstrumentAdmin)


# class AlertItemAdmin(admin.ModelAdmin):
#     list_display = [
#         'id',
#         'instrument',
#         'datum_timestamp',
#         'datum_value',
#         'state',
#         'created_at',
#
#     ]
#     list_filter = ['state',]
#     ordering = ['-id',]
#     raw_id_fields = ['instrument',]
#     readonly_fields = ['id','created_at','slug',]
#
#     # def has_add_permission(self, request, obj=None):
#     #     return False
#     #
#     # def has_delete_permission(self, request, obj=None):
#     #     return False
#
# admin.site.register(AlertItem, AlertItemAdmin)


class InstrumentAnalysisAdmin(admin.ModelAdmin):
    list_display = [
        'id',

    ]
    list_filter = []
    ordering = ['-id',]
    raw_id_fields = ['instrument', 'report',]
    readonly_fields = ['id','created_at',]

    # def has_add_permission(self, request, obj=None):
    #     return False
    #
    # def has_delete_permission(self, request, obj=None):
    #     return False

admin.site.register(InstrumentAnalysis, InstrumentAnalysisAdmin)


class InstrumentSimulatorAdmin(admin.ModelAdmin):
    list_display = [
        'instrument', 'is_running'

    ]
    list_filter = ['is_running',]
    ordering = ['-id',]
    raw_id_fields = ['instrument',]
    readonly_fields = ['id',]

    # def has_add_permission(self, request, obj=None):
    #     return False
    #
    # def has_delete_permission(self, request, obj=None):
    #     return False

admin.site.register(InstrumentSimulator, InstrumentSimulatorAdmin)


class DeviceSimulatorAdmin(admin.ModelAdmin):
    list_display = [
        'device', 'is_running'

    ]
    list_filter = ['is_running',]
    ordering = ['-id',]
    raw_id_fields = ['device',]
    readonly_fields = ['id',]

    # def has_add_permission(self, request, obj=None):
    #     return False
    #
    # def has_delete_permission(self, request, obj=None):
    #     return False

admin.site.register(DeviceSimulator, DeviceSimulatorAdmin)


class TaskItemAdmin(admin.ModelAdmin):
    list_display = ['slug', 'id', 'type_of', 'last_modified_at']
    list_filter = ['type_of',]
    # search_fields = ['device_id',]
    raw_id_fields = ['user',]
    ordering = ['-created_at',]
    readonly_fields = [
        'id', 'created_by', 'created_by', 'created_from', 'created_from_is_public',
        'last_modified_by', 'last_modified_at', 'last_modified_from', 'last_modified_from_is_public'
    ]
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget }
    }

    def save_model(self, request, obj, form, change):
        """
        Override the `save` function in `Django Admin` to include audit details.
        """
        client_ip, is_routable = get_client_ip(request)
        obj.created_by = request.user
        obj.created_from = client_ip
        obj.created_from_is_public = is_routable
        obj.last_modified_by = request.user
        obj.last_modified_from = client_ip
        obj.last_modified_from_is_public = is_routable
        super().save_model(request, obj, form, change)

admin.site.register(TaskItem, TaskItemAdmin)
