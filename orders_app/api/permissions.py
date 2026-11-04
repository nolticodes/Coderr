

from rest_framework import permissions


class IsCustomerAndIsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.type == "customer"


class IsBusinessAndIsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.type == "business"

    def has_object_permission(self, request, view, obj):
        return obj.business_user_id == request.user.id