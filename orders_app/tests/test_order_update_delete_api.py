from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import User
from orders_app.models import Orders

from .helpers import create_order_test_data, create_test_order


class OrderUpdateDeleteApiTests(APITestCase):
    """Test order status changes and staff-only deletion."""

    def setUp(self):
        """Create an order, its participants, another provider, and a staff user."""
        self.customer, self.business, self.detail = (
            create_order_test_data()
        )
        self.order = create_test_order(
            self.customer,
            self.business,
            self.detail,
        )
        self.url = f"/api/orders/{self.order.pk}/"

        self.other_business = User.objects.create_user(
            username="otherbusiness",
            email="otherbusiness@example.com",
            password="Testpasswort123!",
            type="business",
        )
        self.staff = User.objects.create_user(
            username="staffuser",
            email="staff@example.com",
            password="Testpasswort123!",
            type="customer",
            is_staff=True,
        )

    def authenticate(self, user):
        """Authenticate subsequent requests with the supplied user's token."""
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

    def test_assigned_business_can_update_status(self):
        """Update the status and return full order data with a new timestamp."""
        self.authenticate(self.business)
        previous_time = timezone.now() - timedelta(days=1)
        Orders.objects.filter(pk=self.order.pk).update(
            updated_at=previous_time
        )

        response = self.client.patch(
            self.url,
            {"status": "completed"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.order.refresh_from_db()

        self.assertEqual(self.order.status, "completed")
        self.assertGreater(self.order.updated_at, previous_time)
        self.assertEqual(response.data["id"], self.order.pk)
        self.assertEqual(response.data["status"], "completed")
        self.assertEqual(response.data["price"], self.detail.price)
        self.assertEqual(
            response.data["customer_user"],
            self.customer.pk,
        )
        self.assertEqual(
            response.data["business_user"],
            self.business.pk,
        )
        self.assertTrue(response.data["updated_at"])

    def test_customer_cannot_update_status(self):
        """Reject status changes by the customer assigned to the order."""
        self.authenticate(self.customer)

        response = self.client.patch(
            self.url,
            {"status": "completed"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "in_progress")

    def test_other_business_cannot_update_status(self):
        """Reject status changes by a provider not assigned to the order."""
        self.authenticate(self.other_business)

        response = self.client.patch(
            self.url,
            {"status": "completed"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "in_progress")

    def test_anonymous_user_cannot_update_status(self):
        """Reject unauthenticated status changes."""
        response = self.client.patch(
            self.url,
            {"status": "completed"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "in_progress")

    def test_invalid_status_returns_bad_request(self):
        """Reject an unsupported status without changing the order."""
        self.authenticate(self.business)

        response = self.client.patch(
            self.url,
            {"status": "unknown"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("status", response.data)

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "in_progress")

    def test_missing_order_returns_not_found_on_patch(self):
        """Return 404 when an authorized provider requests an unknown order."""
        self.authenticate(self.business)

        response = self.client.patch(
            f"/api/orders/{self.order.pk + 1}/",
            {"status": "completed"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_staff_can_delete_order(self):
        """Allow staff deletion without requiring business status or ownership."""
        self.authenticate(self.staff)
        order_id = self.order.pk

        response = self.client.delete(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertEqual(response.content, b"")
        self.assertFalse(
            Orders.objects.filter(pk=order_id).exists()
        )

        # Deleting the order must preserve the original package and users.
        self.assertTrue(
            self.detail.__class__.objects.filter(
                pk=self.detail.pk
            ).exists()
        )
        self.assertTrue(
            User.objects.filter(pk=self.customer.pk).exists()
        )
        self.assertTrue(
            User.objects.filter(pk=self.business.pk).exists()
        )

    def test_non_staff_users_cannot_delete_order(self):
        """Reject deletion by customers and business users without staff status."""
        for user in [
            self.customer,
            self.business,
            self.other_business,
        ]:
            with self.subTest(user=user.username):
                self.authenticate(user)

                response = self.client.delete(self.url)

                self.assertEqual(
                    response.status_code,
                    status.HTTP_403_FORBIDDEN,
                )
                self.assertTrue(
                    Orders.objects.filter(pk=self.order.pk).exists()
                )

    def test_anonymous_user_cannot_delete_order(self):
        """Reject deletion without authentication."""
        response = self.client.delete(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertTrue(
            Orders.objects.filter(pk=self.order.pk).exists()
        )

    def test_missing_order_returns_not_found_on_delete(self):
        """Return 404 when staff attempts to delete an unknown order."""
        self.authenticate(self.staff)

        response = self.client.delete(
            f"/api/orders/{self.order.pk + 1}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_get_and_put_are_not_allowed(self):
        """Reject methods excluded by the detail view."""
        self.authenticate(self.business)

        get_response = self.client.get(self.url)
        put_response = self.client.put(
            self.url,
            {"status": "completed"},
            format="json",
        )

        self.assertEqual(
            get_response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assertEqual(
            put_response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )