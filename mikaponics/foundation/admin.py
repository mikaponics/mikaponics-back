from ipware import get_client_ip
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
# from django.contrib.auth.admin import UserAdmin

from foundation.models import *


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'is_staff', 'is_active', 'was_email_activated', 'was_onboarded',]
    list_filter = ('is_staff',)

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

        ('Email Activation / Password Reset',
            {'fields': ('was_email_activated', 'pr_access_code', 'pr_expiry_date')}
        ),

        ('Billing Information',
            {'fields': ('billing_given_name', 'billing_last_name', 'billing_email')}
        ),

        ('Shipping Information',
            {'fields': ('shipping_given_name', 'shipping_last_name', 'shipping_email')}
        ),

        ('E-Ecommerce', {'fields': (
            'was_onboarded',
            'customer_id','customer_data', 'subscription_status',
        )}),
    )
    readonly_fields = ['subscription_status',]

    search_fields =  ['email',]
    ordering = ['email',]

    filter_horizontal = ()

admin.site.register(User, UserAdmin)
admin.site.unregister(Group)


class DeviceAdmin(admin.ModelAdmin):
    raw_id_fields = ['user', 'invoice',]
    list_filter = ['product',]
    list_display = ['slug', 'id', 'user_id', 'product',]
    ordering = ['-id',]
    readonly_fields = [
        'uuid', 'created_at', 'created_by', 'created_from',
        'created_from_is_public', 'last_modified_at', 'last_modified_by',
        'last_modified_from', 'last_modified_from_is_public', 'activated_at',
        'last_measured_value', 'last_measured_at',
        'last_measured_unit_of_measure', 'get_environment_variables_file_url',
    ]

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
        'next', 'previous',
    ]

    # def has_add_permission(self, request, obj=None):
    #     return False
    #
    # def has_delete_permission(self, request, obj=None):
    #     return False

admin.site.register(TimeSeriesDatum, TimeSeriesDatumAdmin)


class InstrumentAlertAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'instrument',
        'datum_timestamp',
        'datum_value',
        'state',
        'created_at',

    ]
    list_filter = ['state',]
    ordering = ['-id',]
    raw_id_fields = ['instrument',]
    readonly_fields = ['id','created_at','slug',]

    # def has_add_permission(self, request, obj=None):
    #     return False
    #
    # def has_delete_permission(self, request, obj=None):
    #     return False

admin.site.register(InstrumentAlert, InstrumentAlertAdmin)


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
