from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response

from reviews_app.models import Reviews

from .serializers import GetReviewsListResponseSerializer


class ReviewsListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetReviewsListResponseSerializer
    queryset = Reviews.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()

        business_user_id_param = self.request.query_params.get(
            "business_user_id")
        if business_user_id_param is not None:
            queryset = queryset.filter(business_user_id=business_user_id_param)

        reviewer_user_id_param = self.request.query_params.get(
            "reviewer_id")
        if reviewer_user_id_param is not None:
            queryset = queryset.filter(
                reviewer_id=reviewer_user_id_param)

        ordering_param = self.request.query_params.get(
            "ordering"
        )
        if ordering_param in ["rating", "-rating", "updated_at", "-updated_at"]:
            queryset = queryset.order_by(ordering_param)

        return queryset
