from rest_framework import generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.response import Response

from profile_app.models import Profile

from .serializers import (
    GetProfileDetailsSerializer,
    PatchProfileDetailsRequestSerializer,
    PatchProfileDetailsResponseSerializer,
    GetBusinessProfilesSerializer,
    GetCustomerProfilesSerializer,
)

from .permissions import IsOwnerOrReadOnly


class ProfileDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve profiles by user ID and allow owners to partially update them."""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch", "head", "options"]
    queryset = Profile.objects.all()
    lookup_field = "user_id"
    lookup_url_kwarg = "pk"

    def get_serializer_class(self):
        """Select the request serializer for PATCH and the detail serializer otherwise."""
        if self.request.method == "GET":
            return GetProfileDetailsSerializer

        if self.request.method == "PATCH":
            return PatchProfileDetailsRequestSerializer

        return GetProfileDetailsSerializer

    def get_permissions(self):
        """Require authentication and apply owner permissions to non-GET requests."""
        if self.request.method == "GET":
            return [IsAuthenticated()]

        return [IsAuthenticated(), IsOwnerOrReadOnly()]

    def partial_update(self, request, *args, **kwargs):
        """Validate and save partial profile changes, then return the updated profile."""
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        response_serializer = PatchProfileDetailsResponseSerializer(
            serializer.instance,
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


class GetProfilesBusinessListView(APIView):
    """Provide a list of business profiles to authenticated users."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return profiles whose linked user has the business type."""
        profiles = Profile.objects.filter(user__type="business")

        serializer = GetBusinessProfilesSerializer(
            profiles,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class GetProfilesCustomerListView(APIView):
    """Provide a list of customer profiles to authenticated users."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return profiles whose linked user has the customer type."""
        profiles = Profile.objects.filter(user__type="customer")

        serializer = GetCustomerProfilesSerializer(
            profiles,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
