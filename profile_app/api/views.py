from rest_framework import generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound

from profile_app.models import Profile

from .serializers import GetProfileDetailsSerializer, PatchProfileDetailsSerializer

from .permissions import IsOwnerOrReadOnly


class ProfileDetailsView(generics.RetrieveUpdateDestroyAPIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch", "head", "options"]
    queryset = Profile.objects.all()
    lookup_field = "user_id"
    lookup_url_kwarg = "pk"

    def get_serializer_class(self):
        """Select the appropriate serializer for GET and PATCH requests."""
        if self.request.method == "GET":
            return GetProfileDetailsSerializer

        if self.request.method == "PATCH":
            return PatchProfileDetailsSerializer

        return GetProfileDetailsSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]

        return [IsAuthenticated(), IsOwnerOrReadOnly()]
