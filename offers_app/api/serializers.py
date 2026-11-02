from rest_framework import serializers

from auth_app.models import User
from offers_app.models import Offer

from offers_app.models import OfferDetail


class OfferUserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username"
        ]


class OfferDetailSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return f"/offerdetails/{obj.pk}/"

    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "url"
        ]


class GetOffersListSerializer(serializers.ModelSerializer):
    user_details = OfferUserDetailsSerializer(
        source="user",
        read_only=True,
    )

    details = OfferDetailSerializer(
        read_only=True,
        many=True
    )

    min_price = serializers.IntegerField(read_only=True)
    min_delivery_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
            "user_details"
        ]


class OfferStatsSerializer(serializers.ModelSerializer):
    delivery_time_in_days = serializers.IntegerField(
        source="delivery_time"
    )

    features = serializers.ListField(
        child=serializers.CharField()
    )

    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type"
        ]


class PostNewOfferRequestSerializer(serializers.ModelSerializer):
    details = OfferStatsSerializer(
        many=True
    )

    class Meta:
        model = Offer
        fields = [
            "title",
            "image",
            "description",
            "details"
        ]

    def validate_details(self, value):
        if len(value) != 3:
            raise serializers.ValidationError(
                "Ein Angebot muss genau drei Details enthalten."
            )
        return value

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        new_offer = Offer.objects.create(**validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer = new_offer, **detail_data)
        return new_offer


class PostNewOfferResponseSerializer(serializers.ModelSerializer):

    details = OfferStatsSerializer(
        many=True
    )

    class Meta:
        model = Offer
        fields = [
            "id",
            "title",
            "image",
            "description",
            "details"
        ]
