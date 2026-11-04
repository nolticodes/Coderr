from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from django.db.models import Q

from .serializers import (
    GetOrdersResonseSerializer,
    PostOrderRequestSerializer,
    PostOrderResponseSerializer,
    )

from .permissions import (
    IsCustomerAndIsAuthenticated,
)

from orders_app.models import Orders


class OrderListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsCustomerAndIsAuthenticated]
    serializer_class = GetOrdersResonseSerializer
    queryset = Orders.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GetOrdersResonseSerializer

        if self.request.method == 'POST':
            return PostOrderRequestSerializer

        return GetOrdersResonseSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        user = self.request.user

        return queryset.filter(
            Q(customer_user=user)
            | Q(business_user=user)
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        response_serializer = PostOrderResponseSerializer(
            serializer.instance,
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
