from django.urls import path

from .views import (
    ReviewsListCreateView
    )

urlpatterns = [
    path('reviews/', ReviewsListCreateView.as_view(), name='reviews'),
]