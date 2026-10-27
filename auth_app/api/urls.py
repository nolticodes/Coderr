
from django.urls import path, include

urlpatterns = [
    path('registration/', include('auth_app.api.urls'), name='registration')
]
