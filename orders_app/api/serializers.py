from rest_framework import serializers

from orders_app.models import Orders

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