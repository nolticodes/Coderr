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
