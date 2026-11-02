from rest_framework import permissions

class IsBusinessUser(permissions.BasePermission):
    def has_permission(self, request, obj):
        if request.method == "GET":
            return True

        return (
            request.user.is_authenticated
            and request.user.type == "business"
        )