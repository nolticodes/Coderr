from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer

from .helpers import create_business_user


class OfferPaginationApiTests(APITestCase):
    """Test offer page sizes, navigation, and pagination limits."""

    def setUp(self):
        """Create seven offers to span multiple default pages."""
        self.url = "/api/offers/"
        self.user = create_business_user()

        self.offers = [
            Offer.objects.create(
                user=self.user,
                title=f"Offer {index}",
                description="Pagination test offer.",
                image=None,
            )
            for index in range(7)
        ]

    def test_default_page_size(self):
        """Return six offers and the standard pagination fields."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data),
            {"count", "next", "previous", "results"},
        )
        self.assertEqual(response.data["count"], 7)
        self.assertEqual(len(response.data["results"]), 6)
        self.assertIsNotNone(response.data["next"])
        self.assertIsNone(response.data["previous"])
        self.assertEqual(
            [offer["id"] for offer in response.data["results"]],
            [offer.pk for offer in self.offers[:6]],
        )

    def test_custom_page_size(self):
        """Honor a valid page_size query parameter."""
        response = self.client.get(
            self.url,
            {"page_size": 3},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)
        self.assertEqual(response.data["count"], 7)

    def test_second_page(self):
        """Return the remaining offer with a previous-page link."""
        response = self.client.get(
            self.url,
            {"page": 2},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [offer["id"] for offer in response.data["results"]],
            [self.offers[6].pk],
        )
        self.assertIsNone(response.data["next"])
        self.assertIsNotNone(response.data["previous"])

    def test_invalid_page_returns_not_found(self):
        """Return 404 when the requested page does not exist."""
        response = self.client.get(
            self.url,
            {"page": 999},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_page_size_is_limited_to_one_hundred(self):
        """Cap the requested page size at 100 results."""
        Offer.objects.bulk_create([
            Offer(
                user=self.user,
                title=f"Additional offer {index}",
                description="Pagination limit test.",
                image=None,
            )
            for index in range(94)
        ])

        response = self.client.get(
            self.url,
            {"page_size": 500},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 101)
        self.assertEqual(len(response.data["results"]), 100)
        self.assertIsNotNone(response.data["next"])