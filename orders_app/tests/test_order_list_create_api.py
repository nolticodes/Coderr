from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import User
from orders_app.models import Orders

from .helpers import create_order_test_data, create_test_order


class OrderListCreateApiTests(APITestCase):
    """Test order visibility, creation responses, and creation permissions."""

    def setUp(self):
        """Create participants, a package, and orders with different ownership."""
        self.url = "/api/orders/"
        self.customer, self.business, self.detail = (
            create_order_test_data()
        )

        self.other_customer = User.objects.create_user(
            username="othercustomer",
            email="othercustomer@example.com",
            password="Testpasswort123!",
            type="customer",
        )
        self.other_business = User.objects.create_user(
            username="otherbusiness",
            email="otherbusiness@example.com",
            password="Testpasswort123!",
            type="business",
        )

        self.customer_order = create_test_order(
            self.customer,
            self.other_business,
            self.detail,
        )
        self.business_order = create_test_order(
            self.other_customer,
            self.business,
            self.detail,
        )
        self.unrelated_order = create_test_order(
            self.other_customer,
            self.other_business,
            self.detail,
        )

    def authenticate(self, user):
        """Authenticate subsequent requests with the supplied user's token."""
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

    def get_results(self, response):
        """Extract order results with or without global pagination."""
        if isinstance(response.data, dict):
            return response.data["results"]

        return response.data

    def test_customer_sees_only_their_orders(self):
        """Return only orders in which the current customer participates."""
        self.authenticate(self.customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {order["id"] for order in self.get_results(response)},
            {self.customer_order.pk},
        )

    def test_business_user_sees_only_their_orders(self):
        """Return only orders assigned to the current provider."""
        self.authenticate(self.business)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {order["id"] for order in self.get_results(response)},
            {self.business_order.pk},
        )

    def test_user_without_orders_receives_empty_results(self):
        """Return no orders for an authenticated user without participation."""
        user = User.objects.create_user(
            username="newcustomer",
            email="newcustomer@example.com",
            password="Testpasswort123!",
            type="customer",
        )
        self.authenticate(user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.get_results(response), [])

    def test_anonymous_user_cannot_list_orders(self):
        """Reject order listing without authentication."""
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_customer_can_create_order(self):
        """Create an order from a package and return the complete order data."""
        self.authenticate(self.customer)
        count_before = Orders.objects.count()

        response = self.client.post(
            self.url,
            {"offer_detail_id": self.detail.pk},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(Orders.objects.count(), count_before + 1)

        order = Orders.objects.get(pk=response.data["id"])

        self.assertEqual(order.customer_user_id, self.customer.pk)
        self.assertEqual(order.business_user_id, self.business.pk)
        self.assertEqual(order.offer_detail_id, self.detail.pk)

        self.assertEqual(
            set(response.data),
            {
                "id",
                "customer_user",
                "business_user",
                "title",
                "revisions",
                "delivery_time_in_days",
                "price",
                "features",
                "offer_type",
                "status",
                "created_at",
                "updated_at",
            },
        )
        self.assertEqual(
            response.data["customer_user"],
            self.customer.pk,
        )
        self.assertEqual(
            response.data["business_user"],
            self.business.pk,
        )
        self.assertEqual(response.data["title"], self.detail.title)
        self.assertEqual(
            response.data["revisions"],
            self.detail.revisions,
        )
        self.assertEqual(
            response.data["delivery_time_in_days"],
            self.detail.delivery_time,
        )
        self.assertEqual(response.data["price"], self.detail.price)
        self.assertEqual(
            response.data["features"],
            self.detail.features,
        )
        self.assertEqual(
            response.data["offer_type"],
            self.detail.offer_type,
        )
        self.assertEqual(response.data["status"], "in_progress")
        self.assertTrue(response.data["created_at"])
        self.assertTrue(response.data["updated_at"])

    def test_business_user_cannot_create_order(self):
        """Reject order creation by a business user."""
        self.authenticate(self.business)
        count_before = Orders.objects.count()

        response = self.client.post(
            self.url,
            {"offer_detail_id": self.detail.pk},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(Orders.objects.count(), count_before)

    def test_anonymous_user_cannot_create_order(self):
        """Reject order creation without authentication."""
        count_before = Orders.objects.count()

        response = self.client.post(
            self.url,
            {"offer_detail_id": self.detail.pk},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertEqual(Orders.objects.count(), count_before)

    def test_invalid_creation_input_returns_bad_request(self):
        """Reject missing or malformed package IDs without creating orders."""
        self.authenticate(self.customer)
        count_before = Orders.objects.count()

        for data in [{}, {"offer_detail_id": "invalid"}]:
            with self.subTest(data=data):
                response = self.client.post(
                    self.url,
                    data,
                    format="json",
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_400_BAD_REQUEST,
                )
                self.assertIn("offer_detail_id", response.data)

        self.assertEqual(Orders.objects.count(), count_before)

    def test_unknown_package_returns_not_found(self):
        """Return 404 without creating an order for an unknown package."""
        self.authenticate(self.customer)
        count_before = Orders.objects.count()

        response = self.client.post(
            self.url,
            {"offer_detail_id": self.detail.pk + 1},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(Orders.objects.count(), count_before)