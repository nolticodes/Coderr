from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):

    TYPE_CHOICES = [
        ('customer', "Customer"),
        ('business', 'Business')
    ]

    username = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField()
    type = models.CharField(choices=TYPE_CHOICES, default="customer")
    created_at = models.DateTimeField()
    