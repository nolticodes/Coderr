from django.urls import path

from .views import (
    OfferListCreateView,
    OfferDetailsListCreateDestroyView,
    SpecificOfferDetailView
    )

urlpatterns = [
    path('offers/', OfferListCreateView.as_view(), name='offers-list'),
    path('offers/<int:pk>/', OfferDetailsListCreateDestroyView.as_view(), name='offer-details'),
    (path('offerdetails/<int:pk>/', SpecificOfferDetailView.as_view(), name='specific-offer-details'))
]