from django.contrib.auth.models import Group, Permission
from django.utils.translation import ugettext_lazy as _
from rest_framework import permissions

from foundation.models import Device, Instrument


class CanListCreateDevicePermission(permissions.BasePermission):
    message = _('You do not have permission to access this API-endpoint.')

    def has_permission(self, request, view):
        print("has_permission", request.method)  # For debugging purposes only.

        # --- LIST ---
        if "GET" in request.method:
            # DEVELOPERS NOTE: The `view` will filter the results to the user.
            return True

        # --- CREATE ---
        if "POST" in request.method:
            print(">>>",request.user)
        print("|||",request.user)

        return False


class CanRetrieveUpdateDestroyDevicePermission(permissions.BasePermission):
    message = _('You do not have permission to access this API-endpoint.')

    def has_object_permission(self, request, view, obj):
        print("has_object_permission", request.method)  # For debugging purposes only.

        # # --- RETRIEVE ---
        # if "GET" in request.method:
        #     # OWNERSHIP BASED
        #     if request.user == obj.owner:
        #         return True
        #
        #     # PERMISSION BASED
        #     return has_permission('can_get_associate', request.user, request.user.groups.all())
        #
        # # ---UPDATE ---
        # if "PUT" in request.method:
        #     # OWNERSHIP BASED
        #     if request.user == obj.owner:
        #         return True
        #
        #     # PERMISSION BASED
        #     return has_permission('can_put_associate', request.user, request.user.groups.all())
        #
        # # --- DELETE ---
        # if "DELETE" in request.method:
        #     # PERMISSION BASED
        #     return has_permission('can_delete_associate', request.user, request.user.groups.all())

        return False



class CanListCreateTimeSeriesDatumPermission(permissions.BasePermission):
    message = _('You do not have permission to access this API-endpoint.')

    def has_permission(self, request, view):
        # print("has_permission", request.method)  # For debugging purposes only.

        # --- LIST ---
        if "GET" in request.method:
            # DEVELOPERS NOTE: The `view` will filter the results to the user.
            return True

        # --- CREATE ---
        if "POST" in request.method:
            try:
                instrument_uuid = request.data.get('instrument_uuid', None)
                instrument = Instrument.objects.get(uuid=instrument_uuid)
                return instrument.device.user == request.user
            except Exception:
                pass

        return False


class CanRetrieveUpdateDestroyTimeSeriesDatumPermission(permissions.BasePermission):
    message = _('You do not have permission to access this API-endpoint.')

    def has_object_permission(self, request, view, obj):
        print("has_object_permission", request.method)  # For debugging purposes only.

        # # --- RETRIEVE ---
        # if "GET" in request.method:
        #     # OWNERSHIP BASED
        #     if request.user == obj.owner:
        #         return True
        #
        #     # PERMISSION BASED
        #     return has_permission('can_get_associate', request.user, request.user.groups.all())
        #
        # # ---UPDATE ---
        # if "PUT" in request.method:
        #     # OWNERSHIP BASED
        #     if request.user == obj.owner:
        #         return True
        #
        #     # PERMISSION BASED
        #     return has_permission('can_put_associate', request.user, request.user.groups.all())
        #
        # # --- DELETE ---
        # if "DELETE" in request.method:
        #     # PERMISSION BASED
        #     return has_permission('can_delete_associate', request.user, request.user.groups.all())

        return False
