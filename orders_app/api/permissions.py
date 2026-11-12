from rest_framework import permissions


class IsCustomerAndIsAuthenticated(permissions.BasePermission):
    """Allow authenticated reading and restrict writing to customer users."""

    def has_permission(self, request, view):
        """Require authentication and the customer type for unsafe methods."""
        if not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.type == "customer"


class IsBusinessAndIsAuthenticated(permissions.BasePermission):
    """Require authentication, business status for writing, and order ownership."""

    def has_permission(self, request, view):
        """Require authentication and the business type for unsafe methods."""
        if not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.type == "business"

    def has_object_permission(self, request, view, obj):
        """Restrict object access to the business user assigned to the order."""
        return obj.business_user_id == request.user.id
