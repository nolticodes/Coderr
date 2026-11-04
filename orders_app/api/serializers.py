from rest_framework import serializers

from orders_app.models import Orders
from offers_app.models import OfferDetail

from django.shortcuts import get_object_or_404


class GetOrdersResonseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Orders
        fields = [
            'id',
            'customer_user',
            'business_user',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
            'status',
            'created_at',
            'updated_at'
        ]


class PostOrderRequestSerializer(serializers.Serializer):

    offer_detail_id = serializers.IntegerField()

    def create(self, validated_data):
        offer_detail_id = validated_data["offer_detail_id"]

        offer_detail = get_object_or_404(
            OfferDetail,
            pk=offer_detail_id,
        )

        business_user = offer_detail.offer.user

        customer_user = self.context["request"].user

        order = Orders.objects.create(
            offer_detail_id=offer_detail.pk,
            business_user=business_user,
            customer_user=customer_user,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
            status="in_progress",
        )

        return order


class PostOrderResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Orders
        fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at",
        ]


class PatchOrderDetailRequestSerializer(serializers.ModelSerializer):

    status = serializers.ChoiceField(
        choices=Orders.STATUS_CHOICES
    )

    class Meta:
        model = Orders
        fields = [
            'status'
        ]


