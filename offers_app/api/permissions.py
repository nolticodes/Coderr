from rest_framework import permissions


class IsBusinessUser(permissions.BasePermission):
    """Allow public GET requests and restrict other methods to business users."""

    def has_permission(self, request, view):
        """Allow GET or require an authenticated business user."""
        if request.method == "GET":
            return True

        return (
            request.user.is_authenticated
            and request.user.type == "business"
        )


class IsAuthenticatedAndOwnerOrReadOnly(permissions.BasePermission):
    """Allow authenticated reading and restrict writing to the object owner."""

    def has_permission(self, request, view):
        """Require an authenticated user."""
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Allow safe methods or require ownership of the object."""
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user
