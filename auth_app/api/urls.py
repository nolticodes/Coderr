
from django.urls import path

from .views import (
    RegistrationPostView,
    )

urlpatterns = [
    path('registration/', RegistrationPostView.as_view(), name='registration')
]
