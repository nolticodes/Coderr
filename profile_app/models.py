from django.db import models

from auth_app.models import User

# Create your models here.

class Profile(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=True, default="")
    last_name = models.CharField(max_length=50, blank=True, default="")
    file = models.CharField(max_length=50)
    uploaded_at = models.DateTimeField(null=True, blank=True, editable=False)
    location = models.CharField(max_length=50, blank=True, default="")
    tel = models.CharField(max_length=50, blank=True, default="")
    description = models.TextField(blank=True, default="")
    working_hours = models.CharField(max_length=50)