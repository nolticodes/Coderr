from django.db import models

from auth_app.models import User

# Create your models here.

class Profile(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    file = models.CharField(max_length=50)
    location = models.CharField(max_length=50)
    tel = models.CharField(max_length=50)
    description = models.TextField()
    working_hours = models.CharField(max_length=50)