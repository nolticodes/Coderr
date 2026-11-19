from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from orders_app.models import Orders
from orders_app.api.serializers import (
    PatchOrderDetailRequestSerializer,
)

from .helpers import create_order_test_data, create_test_order


class OrderUpdateSerializerTests(TestCase):
    """Test status validation and preservation of purchased order data."""

    def setUp(self):
        """Create an order with known package values."""
        customer, business, detail = create_order_test_data()
        self.order = create_test_order(customer, business, detail)

    def test_allowed_status_values_are_saved(self):
        """Accept each status defined by the order model."""
        for value, _ in Orders.STATUS_CHOICES:
            with self.subTest(status=value):
                serializer = PatchOrderDetailRequestSerializer(
                    self.order,
                    data={"status": value},
                    partial=True,
                )

                self.assertTrue(
                    serializer.is_valid(),
                    serializer.errors,
                )
                updated_order = serializer.save()
                updated_order.refresh_from_db()

                self.assertEqual(updated_order.status, value)

    def test_invalid_status_values_are_rejected(self):
        """Reject unsupported, empty, and null status values."""
        for value in ["unknown", "", None]:
            with self.subTest(status=value):
                serializer = PatchOrderDetailRequestSerializer(
                    self.order,
                    data={"status": value},
                    partial=True,
                )

                self.assertFalse(serializer.is_valid())
                self.assertIn("status", serializer.errors)

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "in_progress")

    def test_status_update_preserves_other_order_fields(self):
        """Change the status without modifying purchased data or ownership."""
        fields = [
            "customer_user_id",
            "business_user_id",
            "offer_detail_id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "created_at",
        ]
        original_values = {
            field: getattr(self.order, field)
            for field in fields
        }

        serializer = PatchOrderDetailRequestSerializer(
            self.order,
            data={"status": "completed"},
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        self.order.refresh_from_db()

        self.assertEqual(self.order.status, "completed")

        for field, expected in original_values.items():
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(self.order, field),
                    expected,
                )

    def test_status_update_refreshes_updated_at(self):
        """Refresh the modification timestamp when saving a status change."""
        previous_time = timezone.now() - timedelta(days=1)
        Orders.objects.filter(pk=self.order.pk).update(
            updated_at=previous_time
        )
        self.order.refresh_from_db()

        serializer = PatchOrderDetailRequestSerializer(
            self.order,
            data={"status": "completed"},
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        self.order.refresh_from_db()

        self.assertGreater(self.order.updated_at, previous_time)