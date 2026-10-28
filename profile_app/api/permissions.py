from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Erlaubt jedem eingeloggten Nutzer das Lesen (GET).
    Schreiben (PATCH, PUT, DELETE) darf nur der Besitzer des Profils.
    """

    def has_object_permission(self, request, view, obj):
        if request.method == "GET":
            return True

        return obj.user == request.user