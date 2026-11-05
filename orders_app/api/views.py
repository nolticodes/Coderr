from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db.models import Q
from django.shortcuts import get_object_or_404

from .serializers import (
    GetOrdersResonseSerializer,
    PostOrderRequestSerializer,
    PostOrderResponseSerializer,
    PatchOrderDetailRequestSerializer,
)

from .permissions import (
    IsCustomerAndIsAuthenticated,
    IsBusinessAndIsAuthenticated
)

from orders_app.models import Orders
from auth_app.models import User


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


class PatchDeleteOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["patch", "delete"]
    permission_classes = [IsBusinessAndIsAuthenticated]
    serializer_class = PatchOrderDetailRequestSerializer
    lookup_field = "pk"
    lookup_url_kwarg = "pk"
    queryset = Orders.objects.all()

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdminUser()]
        return [IsBusinessAndIsAuthenticated()]

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        response_serializer = PostOrderResponseSerializer(
            serializer.instance,
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK
        )


class GetProgressOrderCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        business_user = get_object_or_404(
            User,
            pk=business_user_id,
            type="business"
        )

        business_user_orders = Orders.objects.filter(business_user=business_user)
        orders_in_progress = business_user_orders.filter(status="in_progress").count()

        return Response ({
            "order_count": orders_in_progress
        })

