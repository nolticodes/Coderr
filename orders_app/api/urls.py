from django.urls import path

from .views import (
        OrderListCreateView
    )

urlpatterns = [
    path('orders/', OrderListCreateView.as_view(), name='orders'),
    # path('offers/<int:pk>/', OfferDetailsListCreateDestroyView.as_view(), name='offer-details'),
]