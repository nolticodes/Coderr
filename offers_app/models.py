from django.db import models

from django.conf import settings

# Create your models here.


class Offer(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    image = models.CharField(blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OfferDetail(models.Model):

    TYPE_CHOICES = [
        ('basic', "Basic"),
        ('standard', 'Standard'),
        ('premium', 'Premium')
    ]

    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name="details",
    )
    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    price = models.IntegerField()
    delivery_time = models.IntegerField()
    features = models.JSONField(default=list)
    offer_type = models.CharField(choices=TYPE_CHOICES, default="basic")
