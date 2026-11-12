from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow GET access and restrict other object operations to the profile owner."""

    def has_object_permission(self, request, view, obj):
        """Allow GET requests or require ownership of the profile."""
        if request.method == "GET":
            return True

        return obj.user == request.user
