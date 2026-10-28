from django.urls import path

from .views import ProfileDetailsView

urlpatterns = [
    path('profile/<int:pk>/', ProfileDetailsView.as_view(), name='authentication'),
]
