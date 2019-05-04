from ipware import get_client_ip
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
# from django.contrib.auth.admin import UserAdmin

from foundation.models import *


class CropAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'type_of'

    ]
    list_filter = ['type_of',]
    ordering = ['order_number',]
    raw_id_fields = []
    readonly_fields = ['id',]

    # def has_add_permission(self, request, obj=None):
    #     return False
    #
    # def has_delete_permission(self, request, obj=None):
    #     return False

admin.site.register(Crop, CropAdmin)



class CropSubstrateAdmin(admin.ModelAdmin):
    list_display = [
        'name',
    ]
    list_filter = []
    ordering = ['order_number',]
    raw_id_fields = []
    readonly_fields = ['id',]

    # def has_add_permission(self, request, obj=None):
    #     return False
    #
    # def has_delete_permission(self, request, obj=None):
    #     return False

admin.site.register(CropSubstrate, CropSubstrateAdmin)


class ProductionCropInline(admin.TabularInline):
    model = ProductionCrop


class ProductionInspectionInline(admin.TabularInline):
    model = ProductionInspection


class ProductionAdmin(admin.ModelAdmin):
    inlines = [
        ProductionCropInline,
        ProductionInspectionInline
    ]
    raw_id_fields = ['user', ]
    list_filter = ['state', 'started_at', 'finished_at', 'grow_system',]
    list_display = ['slug', 'user', 'started_at', 'finished_at', 'state', 'grow_system']
    ordering = ['-id',]
    readonly_fields = [
        'id', 'created_at', 'created_by', 'created_from',
        'created_from_is_public', 'last_modified_at', 'last_modified_by',
        'last_modified_from', 'last_modified_from_is_public',
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


admin.site.register(Production, ProductionAdmin)


class ProductionCropAdmin(admin.ModelAdmin):
    raw_id_fields = ['production', ]
    list_filter = ['crop', 'substrate',]
    list_display = ['slug', 'crop', 'substrate', 'production']
    ordering = ['-id',]
    readonly_fields = [
        'id', 'created_at', 'created_by', 'created_from',
        'created_from_is_public', 'last_modified_at', 'last_modified_by',
        'last_modified_from', 'last_modified_from_is_public',
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


admin.site.register(ProductionCrop, ProductionCropAdmin)


class ProductionInspectionAdmin(admin.ModelAdmin):
    raw_id_fields = ['production', 'production_crop',]
    list_filter = []
    list_display = ['slug', 'production']
    ordering = ['-id',]
    readonly_fields = [
        'id', 'created_at', 'created_by', 'created_from',
        'created_from_is_public', 'last_modified_at', 'last_modified_by',
        'last_modified_from', 'last_modified_from_is_public',
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


admin.site.register(ProductionInspection, ProductionInspectionAdmin)
