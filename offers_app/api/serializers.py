from rest_framework import serializers
from django.db import transaction

from auth_app.models import User
from offers_app.models import Offer, OfferDetail


class OfferUserDetailsSerializer(serializers.ModelSerializer):
    """Serialize the offer creator's name and username."""

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username"
        ]


class OfferDetailSerializer(serializers.ModelSerializer):
    """Serialize an offer detail's ID and relative URL."""

    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        """Return the relative URL for the offer detail."""
        return f"/offerdetails/{obj.pk}/"

    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "url"
        ]


class GetOffersListSerializer(serializers.ModelSerializer):
    """Serialize offers with detail links, creator data, and annotated minima."""

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
    """Serialize and validate the fields of an individual offer package."""

    delivery_time_in_days = serializers.IntegerField(
        source="delivery_time"
    )

    features = serializers.ListField(
        child=serializers.CharField()
    )

    revisions = serializers.IntegerField(required=False)

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
    """Validate new offer data and create its nested packages."""

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
        """Require exactly three offer details."""
        if len(value) != 3:
            raise serializers.ValidationError(
                "Ein Angebot muss genau drei Details enthalten."
            )
        return value

    def create(self, validated_data):
        """Create the offer and its details, applying revision defaults by type."""
        details_data = validated_data.pop("details")
        default_revisions = {
            "basic": 2,
            "standard": 5,
            "premium": 10,
        }

        new_offer = Offer.objects.create(**validated_data)

        for detail_data in details_data:
            detail_data.setdefault(
                "revisions",
                default_revisions[detail_data["offer_type"]],
            )

            OfferDetail.objects.create(
                offer=new_offer,
                **detail_data,
            )

        return new_offer


class PostNewOfferResponseSerializer(serializers.ModelSerializer):
    """Serialize a saved offer with its full package details."""

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


class GetOfferDetailsSerializer(serializers.ModelSerializer):
    """Serialize a single offer with its creator ID and detail links."""

    details = OfferDetailSerializer(
        many=True,
        read_only=True
    )

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
        ]


class PatchOfferDetailsRequestSerializer(serializers.ModelSerializer):
    """Validate partial offer changes and update packages by offer type."""

    details = OfferStatsSerializer(
        many=True,
    )

    class Meta:
        model = Offer
        fields = [
            "title",
            "details"
        ]

    @transaction.atomic
    def update(self, instance, validated_data):
        """Atomically update supplied packages and the offer's own fields."""
        details_data = validated_data.pop("details", [])

        for detail_data in details_data:
            offer_type = detail_data.get("offer_type")

            if offer_type is None:
                raise serializers.ValidationError({
                    "details": "Please submit the offer_type for change."
                })

            detail = instance.details.get(offer_type=offer_type)

            for field, value in detail_data.items():
                setattr(detail, field, value)

            detail.save()

        if hasattr(instance, "_prefetched_objects_cache"):
            instance._prefetched_objects_cache.pop("details", None)

        return super().update(instance, validated_data)
