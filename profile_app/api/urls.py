from django.urls import path

from .views import (
    ProfileDetailsView,
    GetProfilesBusinessListView,
    GetProfilesCustomerListView,
    )

urlpatterns = [
    path('profile/<int:pk>/', ProfileDetailsView.as_view(), name='authentication'),
    path('profiles/business/', GetProfilesBusinessListView.as_view(), name="business-profiles"),
    path('profiles/customer/', GetProfilesCustomerListView.as_view(), name="customer-profiles"),
]

