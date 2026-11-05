from django.urls import path

from .views import (
        OrderListCreateView,
        PatchDeleteOrderDetailView,
        GetProgressOrderCountView,
        GetCompletedOrderCountView
    )

urlpatterns = [
    path('orders/', OrderListCreateView.as_view(), name='orders'),
    path('orders/<int:pk>/', PatchDeleteOrderDetailView.as_view(), name='order-details'),
    path('order-count/<int:business_user_id>/', GetProgressOrderCountView.as_view(), name='progress-order-count'),
    path('completed-order-count/<int:business_user_id>/', GetCompletedOrderCountView.as_view(), name='completed-order-count'),
]