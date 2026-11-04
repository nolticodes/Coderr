from django.db import models

from auth_app.models import User

from offers_app.models import OfferDetail

# Create your models here.


class Orders(models.Model):

    STATUS_CHOICES = [
        ('in_progress', "In_Progress"),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    TYPE_CHOICES = [
        ('basic', "Basic"),
        ('standard', 'Standard'),
        ('premium', 'Premium')
    ]

    customer_user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="customer_orders",)
    business_user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="business_orders")
    title = models.CharField(max_length=50)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.IntegerField()
    features = models.JSONField(default=list)
    offer_type = models.CharField(choices=TYPE_CHOICES)
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default="in_progress")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    offer_detail = models.ForeignKey(
        OfferDetail,
        on_delete=models.PROTECT,
        related_name="orders",
        null=True,
        blank=True,
    )
