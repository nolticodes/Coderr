from rest_framework import serializers

from reviews_app.models import Reviews


class GetReviewsListResponseSerializer(serializers.ModelSerializer):
    """Serialize reviews with participant IDs, ratings, and timestamps."""

    class Meta:
        model = Reviews
        fields = [
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at",
        ]


class PostReviewRequestSerializer(serializers.ModelSerializer):
    """Validate the reviewed user, rating, and description for a new review."""

    class Meta:
        model = Reviews
        fields = [
            "business_user",
            "rating",
            "description",
        ]


class PostReviewResponseSerializer(serializers.ModelSerializer):
    """Serialize a newly created review with its author and timestamps."""

    class Meta:
        model = Reviews
        fields = [
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at",
        ]


class PatchReviewDetailRequestView(serializers.ModelSerializer):
    """Validate and update a review's rating and description."""

    class Meta:
        model = Reviews
        fields = [
            "rating",
            "description",
        ]


class PatchReviewDetailResponseView(serializers.ModelSerializer):
    """Serialize an updated review with participant IDs and timestamps."""

    class Meta:
        model = Reviews
        fields = [
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at",
        ]
