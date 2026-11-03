from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from django.db.models import Q

from .serializers import GetOrdersResonseSerializer

from orders_app.models import Orders


class OrderListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetOrdersResonseSerializer
    queryset = Orders.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GetOrdersResonseSerializer

        return GetOrdersResonseSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        user = self.request.user

        return queryset.filter(
            Q(customer_user=user)
            | Q(business_user=user)
        )
