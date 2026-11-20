from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from profile_app.models import Profile

from .helpers import create_user_with_profile


class ProfileListApiTests(APITestCase):
    """Test profile lists, user-type filtering, and response fields."""

    def setUp(self):
        """Create customer and business profiles and authenticate a customer."""
        self.business_url = "/api/profiles/business/"
        self.customer_url = "/api/profiles/customer/"

        self.customer, self.customer_profile = (
            create_user_with_profile("customer")
        )
        self.other_customer, _ = create_user_with_profile(
            "othercustomer"
        )
        self.business, self.business_profile = (
            create_user_with_profile("business", "business")
        )
        self.other_business, _ = create_user_with_profile(
            "otherbusiness",
            "business",
        )

        token, _ = Token.objects.get_or_create(user=self.customer)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

    def test_business_list_contains_only_business_profiles(self):
        """Return all business profiles and exclude customer profiles."""
        response = self.client.get(self.business_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {profile["user"] for profile in response.data},
            {self.business.pk, self.other_business.pk},
        )

        for profile in response.data:
            self.assertEqual(profile["type"], "business")

    def test_customer_list_contains_only_customer_profiles(self):
        """Return all customer profiles and exclude business profiles."""
        response = self.client.get(self.customer_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {profile["user"] for profile in response.data},
            {self.customer.pk, self.other_customer.pk},
        )

        for profile in response.data:
            self.assertEqual(profile["type"], "customer")

    def test_business_profile_response_fields(self):
        """Return the expected business profile fields and linked username."""
        response = self.client.get(self.business_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        profile = next(
            item
            for item in response.data
            if item["user"] == self.business.pk
        )

        self.assertEqual(
            set(profile),
            {
                "user",
                "username",
                "first_name",
                "last_name",
                "file",
                "location",
                "tel",
                "description",
                "working_hours",
                "type",
            },
        )
        self.assertEqual(profile["username"], self.business.username)
        self.assertEqual(profile["location"], "Berlin")

    def test_customer_profile_response_fields(self):
        """Return the expected customer fields and the upload timestamp."""
        response = self.client.get(self.customer_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        profile = next(
            item
            for item in response.data
            if item["user"] == self.customer.pk
        )

        self.assertEqual(
            set(profile),
            {
                "user",
                "username",
                "first_name",
                "last_name",
                "file",
                "uploaded_at",
                "type",
            },
        )
        self.assertEqual(profile["username"], self.customer.username)
        self.assertIsNone(profile["uploaded_at"])

    def test_empty_profile_lists_return_empty_arrays(self):
        """Return empty lists when no profiles exist."""
        Profile.objects.all().delete()

        for url in [self.business_url, self.customer_url]:
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertEqual(
                    response.status_code,
                    status.HTTP_200_OK,
                )
                self.assertEqual(response.data, [])

    def test_anonymous_users_cannot_access_profile_lists(self):
        """Require authentication for both profile list endpoints."""
        self.client.credentials()

        for url in [self.business_url, self.customer_url]:
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertEqual(
                    response.status_code,
                    status.HTTP_401_UNAUTHORIZED,
                )