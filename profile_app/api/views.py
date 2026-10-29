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
    GetCustomerProfilesSerializer
    )

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
            return PatchProfileDetailsRequestSerializer

        return GetProfileDetailsSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]

        return [IsAuthenticated(), IsOwnerOrReadOnly()]

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        response_serializer = PatchProfileDetailsResponseSerializer(
            serializer.instance,
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK
        )


class GetProfilesBusinessListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        profiles = Profile.objects.filter(user__type="business")

        serializer = GetBusinessProfilesSerializer(
            profiles,
            many = True,
            )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class GetProfilesCustomerListView(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profiles = Profile.objects.filter(user__type="customer")

        serializer = GetCustomerProfilesSerializer(
            profiles,
            many = True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
        


    

