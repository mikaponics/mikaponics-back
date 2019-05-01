from ipware import get_client_ip
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
# from django.contrib.auth.admin import UserAdmin

from foundation.models import *


class StoreAdmin(admin.ModelAdmin):
    """
    Admin instance which is restriected to forbid deletion and creation of
    any stores. Instance allows admins of the system to modify the runtime
    settings of the store.
    """
    list_display = ['name', 'currency', 'timezone_name',]
    list_filter = []
    # search_fields = ['device_id',]
    raw_id_fields = []
    ordering = ['id']
    readonly_fields = [
        'id',
    ]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Store, StoreAdmin)


class ShipperAdmin(admin.ModelAdmin):

    list_display = ['name',]
    list_filter = []
    # search_fields = ['device_id',]
    raw_id_fields = []
    ordering = ['id']
    readonly_fields = [
        'id',
    ]

admin.site.register(Shipper, ShipperAdmin)


class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'slug', 'number', 'state', 'user', 'created_at', 'last_modified_at',
    ]
    list_filter = []
    # search_fields = ['device_id',]
    raw_id_fields = ['user',]
    ordering = ['number']
    readonly_fields = [
        'number', 'created_at', 'created_by', 'created_from',
        'created_from_is_public', 'last_modified_at', 'last_modified_by',
        'last_modified_from', 'last_modified_from_is_public',
        'payment_merchant_receipt_id', 'payment_merchant_receipt_data',
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

admin.site.register(Invoice, InvoiceAdmin)


class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'invoice', 'product', 'unit_price', 'quantity', 'total_price'
    ]
    list_filter = []
    # search_fields = ['device_id',]
    raw_id_fields = ['invoice', 'product']
    ordering = ['id']
    readonly_fields = [
        'id',
    ]

admin.site.register(InvoiceItem, InvoiceItemAdmin)


class ProductAdmin(admin.ModelAdmin):
    """
    Class will grant access to only update the `Product` model.
    """
    list_display = ['name', 'price']
    list_filter = []
    # search_fields = ['device_id',]
    raw_id_fields = []
    ordering = ['id']
    readonly_fields = []

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Product, ProductAdmin)


class PaymentEventAdmin(admin.ModelAdmin):

    list_display = ['id', 'event_id', 'type', 'created', 'livemode',]
    list_filter = ['type', 'livemode', 'object', 'pending_webhooks', 'api_version',]
    search_fields = ['data', 'event_id', 'request',]
    raw_id_fields = []
    ordering = ['-id']
    readonly_fields = [
        'id',
        'created_at',
        'created_from',
        'created_from_is_public',
        'last_modified_at',
    ]

admin.site.register(PaymentEvent, PaymentEventAdmin)


class CouponAdmin(admin.ModelAdmin):

    list_display = ['id', 'credit', 'belongs_to', 'state',  'expires_at', 'created_at',]
    list_filter = []
    # search_fields = ['device_id',]
    raw_id_fields = ['belongs_to',]
    ordering = ['id']
    readonly_fields = [
        'id',
    ]

admin.site.register(Coupon, CouponAdmin)
