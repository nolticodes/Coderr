from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response

from reviews_app.models import Reviews

from .serializers import (
    GetReviewsListResponseSerializer,
    PostReviewRequestSerializer,
    PostReviewResponseSerializer,
    PatchReviewDetailRequestView,
    PatchReviewDetailResponseView,
)

from .permissions import (
    IsCustomerAndIsAuthenticated,
    IsOwner,
)


class ReviewsListCreateView(generics.ListCreateAPIView):
    """List reviews for authenticated users and allow customers to create reviews."""

    serializer_class = GetReviewsListResponseSerializer
    queryset = Reviews.objects.all()

    def get_serializer_class(self):
        """Select the creation serializer for POST and the list serializer otherwise."""
        if self.request.method == "GET":
            return GetReviewsListResponseSerializer

        if self.request.method == "POST":
            return PostReviewRequestSerializer

        return GetReviewsListResponseSerializer

    def get_permissions(self):
        """Require authentication for reading and customer status for creation."""
        if self.request.method == "GET":
            return [IsAuthenticated()]

        if self.request.method == "POST":
            return [IsCustomerAndIsAuthenticated()]

        return [IsAuthenticated()]

    def get_queryset(self):
        """Filter reviews by provider and author, and apply an allowed ordering."""
        queryset = super().get_queryset()

        business_user_id_param = self.request.query_params.get(
            "business_user_id"
        )
        if business_user_id_param is not None:
            queryset = queryset.filter(
                business_user_id=business_user_id_param
            )

        reviewer_user_id_param = self.request.query_params.get(
            "reviewer_id"
        )
        if reviewer_user_id_param is not None:
            queryset = queryset.filter(
                reviewer_id=reviewer_user_id_param
            )

        ordering_param = self.request.query_params.get(
            "ordering"
        )
        if ordering_param in ["rating", "-rating", "updated_at", "-updated_at"]:
            queryset = queryset.order_by(ordering_param)

        return queryset

    def create(self, request, *args, **kwargs):
        """Create a review attributed to the current user and return its details."""
        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)

        serializer.save(reviewer=request.user)

        response_serializer = PostReviewResponseSerializer(
            serializer.instance,
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class PatchDeleteReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Restrict review retrieval, updates, and deletion to the review's author."""

    permission_classes = [IsOwner]
    queryset = Reviews.objects.all()
    lookup_field = "pk"
    lookup_url_kwarg = "pk"
    serializer_class = PatchReviewDetailRequestView

    def partial_update(self, request, *args, **kwargs):
        """Validate partial review changes and return the updated review details."""
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        response_serializer = PatchReviewDetailResponseView(
            serializer.instance,
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )
