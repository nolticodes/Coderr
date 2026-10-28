
from django.urls import path

from .views import (
    RegistrationPostView,
    LoginPostView
    )

urlpatterns = [
    path('registration/', RegistrationPostView.as_view(), name='registration'),
    path('login/', LoginPostView.as_view(), name="login")
]
