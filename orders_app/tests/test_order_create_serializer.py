from types import SimpleNamespace

from django.http import Http404
from django.test import TestCase

from orders_app.models import Orders
from orders_app.api.serializers import PostOrderRequestSerializer

from .helpers import create_order_test_data


class OrderCreateSerializerTests(TestCase):
    """Test order input validation and creation from an existing package."""

    def setUp(self):
        """Create package data and a request context for the customer."""
        self.customer, self.business, self.detail = (
            create_order_test_data()
        )
        self.context = {
            "request": SimpleNamespace(user=self.customer),
        }

    def build_serializer(self, data):
        """Create an order request serializer with customer context."""
        return PostOrderRequestSerializer(
            data=data,
            context=self.context,
        )

    def test_create_order_from_package(self):
        """Copy package data and assign the correct customer and provider."""
        serializer = self.build_serializer({
            "offer_detail_id": self.detail.pk,
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)
        order = serializer.save()

        self.assertEqual(Orders.objects.count(), 1)
        self.assertEqual(serializer.instance, order)

        order.refresh_from_db()

        self.assertEqual(order.customer_user_id, self.customer.pk)
        self.assertEqual(order.business_user_id, self.business.pk)
        self.assertEqual(order.offer_detail_id, self.detail.pk)
        self.assertEqual(order.title, self.detail.title)
        self.assertEqual(order.revisions, self.detail.revisions)
        self.assertEqual(
            order.delivery_time_in_days,
            self.detail.delivery_time,
        )
        self.assertEqual(order.price, self.detail.price)
        self.assertEqual(order.features, self.detail.features)
        self.assertEqual(order.offer_type, self.detail.offer_type)
        self.assertEqual(order.status, "in_progress")
        self.assertIsNotNone(order.created_at)
        self.assertIsNotNone(order.updated_at)

    def test_missing_detail_id_is_rejected(self):
        """Require an offer detail ID before creating an order."""
        serializer = self.build_serializer({})

        self.assertFalse(serializer.is_valid())
        self.assertIn("offer_detail_id", serializer.errors)
        self.assertEqual(Orders.objects.count(), 0)

    def test_invalid_detail_id_values_are_rejected(self):
        """Reject non-integer, empty, and null detail IDs."""
        for value in ["invalid", "", None, 1.5]:
            with self.subTest(value=value):
                serializer = self.build_serializer({
                    "offer_detail_id": value,
                })

                self.assertFalse(serializer.is_valid())
                self.assertIn("offer_detail_id", serializer.errors)

        self.assertEqual(Orders.objects.count(), 0)

    def test_unknown_detail_raises_not_found(self):
        """Raise Http404 without saving an order for an unknown package."""
        missing_id = self.detail.pk + 1
        serializer = self.build_serializer({
            "offer_detail_id": missing_id,
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)

        with self.assertRaises(Http404):
            serializer.save()

        self.assertEqual(Orders.objects.count(), 0)

    def test_order_preserves_original_package_values(self):
        """Keep purchased values unchanged after the source package changes."""
        serializer = self.build_serializer({
            "offer_detail_id": self.detail.pk,
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        order = serializer.save()

        self.detail.title = "Changed package"
        self.detail.revisions = 10
        self.detail.delivery_time = 20
        self.detail.price = 999
        self.detail.features = ["Different feature"]
        self.detail.save()

        order.refresh_from_db()

        self.assertEqual(order.title, "Basic design")
        self.assertEqual(order.revisions, 2)
        self.assertEqual(order.delivery_time_in_days, 5)
        self.assertEqual(order.price, 100)
        self.assertEqual(order.features, ["Logo", "Business card"])

    def test_request_cannot_override_order_values(self):
        """Use authenticated ownership and package data instead of extra input."""
        serializer = self.build_serializer({
            "offer_detail_id": self.detail.pk,
            "customer_user": self.business.pk,
            "business_user": self.customer.pk,
            "price": 1,
            "status": "completed",
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)
        order = serializer.save()

        self.assertEqual(order.customer_user_id, self.customer.pk)
        self.assertEqual(order.business_user_id, self.business.pk)
        self.assertEqual(order.price, self.detail.price)
        self.assertEqual(order.status, "in_progress")