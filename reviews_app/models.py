from django.db import models

from auth_app.models import User

# Create your models here.


class Reviews(models.Model):

    RATING_CHOICES = [
        (1, 'very bad'),
        (2, 'bad'),
        (3, 'ok'),
        (4, 'good'),
        (5, 'very good')
    ]
    
    business_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="received_reviews",)
    reviewer = models.ForeignKey(User, on_delete=models.PROTECT, related_name='written_reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    description = models.TextField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)