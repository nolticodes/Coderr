from django.urls import path

from .views import (
    ReviewsListCreateView,
    PatchDeleteReviewDetailView
    )

urlpatterns = [
    path('reviews/', ReviewsListCreateView.as_view(), name='reviews'),
    path('reviews/<int:pk>/', PatchDeleteReviewDetailView.as_view(), name='review_details')
]