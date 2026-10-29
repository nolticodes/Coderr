from django.urls import path

from .views import (
    GetOffersListView,
    )

urlpatterns = [
    path('offers/', GetOffersListView.as_view(), name='offers-list'),
]