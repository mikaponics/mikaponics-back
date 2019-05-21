from ipware import get_client_ip
from prettyjson import PrettyJSONWidget
from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import Group
# from django.contrib.auth.admin import UserAdmin

from foundation.models import *


class CropLifeCycleStageAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'type_of'

    ]
    list_filter = ['type_of',]
    ordering = ['order_number',]
    raw_id_fields = []
    readonly_fields = ['id',]
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget }
    }

    # def has_add_permission(self, request, obj=None):
    #     return False
    #
    # def has_delete_permission(self, request, obj=None):
    #     return False

admin.site.register(CropLifeCycleStage, CropLifeCycleStageAdmin)



class CropConditionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'data_sheet', 'type_of', 'stage',

    ]
    list_filter = ['stage', 'data_sheet']
    ordering = ['id',]
    raw_id_fields = []
    readonly_fields = ['id',]
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget }
    }

    # def has_add_permission(self, request, obj=None):
    #     return False
    #
    # def has_delete_permission(self, request, obj=None):
    #     return False

admin.site.register(CropCondition, CropConditionAdmin)



class CropDataSheetAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'type_of'

    ]
    list_filter = ['type_of',]
    ordering = ['order_number',]
    raw_id_fields = []
    readonly_fields = ['id',]
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget }
    }

    # def has_add_permission(self, request, obj=None):
    #     return False
    #
    # def has_delete_permission(self, request, obj=None):
    #     return False

admin.site.register(CropDataSheet, CropDataSheetAdmin)



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


class ProductionAdmin(admin.ModelAdmin):
    inlines = [
        ProductionCropInline,
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


class ProductionCropInspectionInline(admin.TabularInline):
    model = ProductionCropInspection


class ProductionCropAdmin(admin.ModelAdmin):
    inlines = [
        ProductionCropInspectionInline
    ]
    raw_id_fields = ['production', ]
    list_filter = ['data_sheet', 'substrate', 'stage', 'type_of',]
    list_display = ['slug', 'data_sheet', 'data_sheet_other', 'quantity', 'substrate', 'substrate_other', 'stage', 'type_of', 'production', 'evaluation_score', 'evaluation_error']
    ordering = ['-id',]
    readonly_fields = [
        'id', 'created_at', 'created_by', 'created_from',
        'created_from_is_public', 'last_modified_at', 'last_modified_by',
        'last_modified_from', 'last_modified_from_is_public',
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


admin.site.register(ProductionCrop, ProductionCropAdmin)



class ProductionCropInspectionInline(admin.TabularInline):
    model = ProductionCropInspection



class ProductionInspectionAdmin(admin.ModelAdmin):
    inlines = [
        ProductionCropInspectionInline,
    ]
    raw_id_fields = ['production',]
    list_filter = ['did_pass', 'state',]
    list_display = ['slug', 'production', 'did_pass', 'created_at', 'state',]
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



class ProductionCropInspectionAdmin(admin.ModelAdmin):
    raw_id_fields = ['production_crop',]
    list_filter = ['state', 'review', 'stage',]
    list_display = ['slug', 'state', 'review', 'stage',]
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


admin.site.register(ProductionCropInspection, ProductionCropInspectionAdmin)
