from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import User

from .helpers import create_order_test_data, create_test_order


class OrderCountApiTests(APITestCase):
    """Test ongoing and completed order counts for business users."""

    def setUp(self):
        """Create orders with mixed statuses for two business users."""
        self.customer, self.business, self.detail = (
            create_order_test_data()
        )
        self.other_business = User.objects.create_user(
            username="otherbusiness",
            email="otherbusiness@example.com",
            password="Testpasswort123!",
            type="business",
        )

        self.endpoints = [
            (
                "/api/order-count/{}/",
                "order_count",
                2,
            ),
            (
                "/api/completed-order-count/{}/",
                "completed_order_count",
                1,
            ),
        ]

        for order_status in [
            "in_progress",
            "in_progress",
            "completed",
            "cancelled",
        ]:
            order = create_test_order(
                self.customer,
                self.business,
                self.detail,
            )
            order.status = order_status
            order.save()

        for order_status in ["in_progress", "completed"]:
            order = create_test_order(
                self.customer,
                self.other_business,
                self.detail,
            )
            order.status = order_status
            order.save()

        self.authenticate(self.customer)

    def authenticate(self, user):
        """Authenticate subsequent requests with the supplied user's token."""
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

    def test_counts_match_provider_and_status(self):
        """Count only matching statuses belonging to the requested provider."""
        for template, key, expected in self.endpoints:
            with self.subTest(endpoint=key):
                response = self.client.get(
                    template.format(self.business.pk)
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_200_OK,
                )
                self.assertEqual(response.data, {key: expected})

    def test_business_without_orders_receives_zero(self):
        """Return zero rather than 404 for an existing provider without orders."""
        business = User.objects.create_user(
            username="newbusiness",
            email="newbusiness@example.com",
            password="Testpasswort123!",
            type="business",
        )

        for template, key, _ in self.endpoints:
            with self.subTest(endpoint=key):
                response = self.client.get(
                    template.format(business.pk)
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_200_OK,
                )
                self.assertEqual(response.data, {key: 0})

    def test_unknown_user_returns_not_found(self):
        """Return 404 when the requested user does not exist."""
        missing_id = User.objects.order_by("-pk").first().pk + 1

        for template, key, _ in self.endpoints:
            with self.subTest(endpoint=key):
                response = self.client.get(
                    template.format(missing_id)
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_404_NOT_FOUND,
                )

    def test_customer_id_returns_not_found(self):
        """Return 404 when the requested user is not a business user."""
        for template, key, _ in self.endpoints:
            with self.subTest(endpoint=key):
                response = self.client.get(
                    template.format(self.customer.pk)
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_404_NOT_FOUND,
                )

    def test_anonymous_requests_are_rejected(self):
        """Require authentication for both count endpoints."""
        self.client.credentials()

        for template, key, _ in self.endpoints:
            with self.subTest(endpoint=key):
                response = self.client.get(
                    template.format(self.business.pk)
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_401_UNAUTHORIZED,
                )