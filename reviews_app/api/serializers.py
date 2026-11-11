from rest_framework import serializers

from reviews_app.models import Reviews


class GetReviewsListResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reviews
        fields = [
            'id',
            'business_user',
            'reviewer',
            'rating',
            'description',
            'created_at',
            'updated_at'
        ]


class PostReviewRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reviews
        fields = [
            'business_user',
            'rating',
            'description'
        ]


class PostReviewResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reviews
        fields = [
            'id',
            'business_user',
            'reviewer',
            'rating',
            'description',
            'created_at',
            'updated_at'
        ]


class PatchReviewDetailRequestView(serializers.ModelSerializer):

    class Meta:
        model = Reviews
        fields = [
            'rating',
            'description'
        ]


class PatchReviewDetailResponseView(serializers.ModelSerializer):

    class Meta:
        model = Reviews
        fields = [
            'id',
            'business_user',
            'reviewer',
            'rating',
            'description',
            'created_at',
            'updated_at'
        ]
