from django.urls import path

from .views import (
    OfferListCreateView,
    OfferDetailsListCreateDestroyView
    )

urlpatterns = [
    path('offers/', OfferListCreateView.as_view(), name='offers-list'),
    path('offers/<int:pk>/', OfferDetailsListCreateDestroyView.as_view(), name='offer-details')
]