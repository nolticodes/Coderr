from django.urls import path

from .views import (
        OrderListCreateView,
        PatchDeleteOrderDetailView,
        GetProgressOrderCountView
    )

urlpatterns = [
    path('orders/', OrderListCreateView.as_view(), name='orders'),
    path('orders/<int:pk>/', PatchDeleteOrderDetailView.as_view(), name='order-details'),
    path('orders/<int:business_user_id>/', GetProgressOrderCountView.as_view(), name='progress-order-count')
]