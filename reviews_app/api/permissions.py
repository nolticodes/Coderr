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


class IsOwner(permissions.BasePermission):
    """Restrict review access to the authenticated author."""

    def has_permission(self, request, view):
        """Require an authenticated user."""
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Allow access only to the user who wrote the review."""
        return obj.reviewer_id == request.user.id
