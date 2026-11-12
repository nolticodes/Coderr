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
    IsBusinessAndIsAuthenticated,
)

from orders_app.models import Orders
from auth_app.models import User


class OrderListCreateView(generics.ListCreateAPIView):
    """List the current user's orders and allow customers to create orders."""

    permission_classes = [IsCustomerAndIsAuthenticated]
    serializer_class = GetOrdersResonseSerializer
    queryset = Orders.objects.all()

    def get_serializer_class(self):
        """Select the request serializer for POST and the list serializer otherwise."""
        if self.request.method == "GET":
            return GetOrdersResonseSerializer

        if self.request.method == "POST":
            return PostOrderRequestSerializer

        return GetOrdersResonseSerializer

    def get_queryset(self):
        """Return orders involving the current user as customer or provider."""
        queryset = super().get_queryset()

        user = self.request.user

        return queryset.filter(
            Q(customer_user=user)
            | Q(business_user=user)
        )

    def create(self, request, *args, **kwargs):
        """Validate the selected package, create an order, and return its details."""
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
            status=status.HTTP_201_CREATED,
        )


class PatchDeleteOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Allow assigned business users to update orders and staff users to delete them."""

    http_method_names = ["patch", "delete"]
    permission_classes = [IsBusinessAndIsAuthenticated]
    serializer_class = PatchOrderDetailRequestSerializer
    lookup_field = "pk"
    lookup_url_kwarg = "pk"
    queryset = Orders.objects.all()

    def get_permissions(self):
        """Require staff status for DELETE and business permissions otherwise."""
        if self.request.method == "DELETE":
            return [IsAdminUser()]

        return [IsBusinessAndIsAuthenticated()]

    def partial_update(self, request, *args, **kwargs):
        """Validate and update the order status, then return the full order."""
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        response_serializer = PostOrderResponseSerializer(
            serializer.instance,
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


class GetProgressOrderCountView(APIView):
    """Provide the number of ongoing orders for a business user."""

    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Return the ongoing order count or 404 if the business user is not found."""
        business_user = get_object_or_404(
            User,
            pk=business_user_id,
            type="business",
        )

        business_user_orders = Orders.objects.filter(
            business_user=business_user,
        )
        orders_in_progress = business_user_orders.filter(
            status="in_progress",
        ).count()

        return Response({
            "order_count": orders_in_progress,
        })


class GetCompletedOrderCountView(APIView):
    """Provide the number of completed orders for a business user."""

    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Return the completed order count or 404 if the business user is not found."""
        business_user = get_object_or_404(
            User,
            pk=business_user_id,
            type="business",
        )

        business_user_orders = Orders.objects.filter(
            business_user=business_user,
        )
        orders_completed = business_user_orders.filter(
            status="completed",
        ).count()

        return Response({
            "completed_order_count": orders_completed,
        })
