from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import User
from offers_app.models import Offer, OfferDetail

from .helpers import create_business_user


class OfferListApiTests(APITestCase):
    """Test offer filtering, calculated minima, and list response data."""

    def setUp(self):
        """Create offers with different creators, prices, and delivery times."""
        self.url = "/api/offers/"
        self.business = create_business_user()
        self.other_business = User.objects.create_user(
            username="otherbusiness",
            email="other@example.com",
            password="Testpasswort123!",
            type="business",
        )

        self.cheap_offer = self.create_offer(
            self.business,
            title="Website Design",
            description="A professional website.",
            prices=[50, 150, 300],
            delivery_times=[3, 7, 14],
        )
        self.expensive_offer = self.create_offer(
            self.other_business,
            title="Branding Package",
            description="Includes website consulting.",
            prices=[200, 300, 400],
            delivery_times=[7, 10, 14],
        )
        self.logo_offer = self.create_offer(
            self.business,
            title="Logo Design",
            description="A custom company logo.",
            prices=[100, 200, 300],
            delivery_times=[5, 8, 12],
        )

    def create_offer(
        self,
        user,
        title,
        description,
        prices,
        delivery_times,
    ):
        """Create an offer with three packages using explicit test values."""
        offer = Offer.objects.create(
            user=user,
            title=title,
            description=description,
            image=None,
        )

        for index, offer_type in enumerate(
            ["basic", "standard", "premium"]
        ):
            OfferDetail.objects.create(
                offer=offer,
                title=f"{offer_type.title()} package",
                revisions=2,
                price=prices[index],
                delivery_time=delivery_times[index],
                features=["Design"],
                offer_type=offer_type,
            )

        return offer

    def get_result_ids(self, params):
        """Request filtered offers and return the IDs on the first page."""
        response = self.client.get(self.url, params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        return {
            offer["id"]
            for offer in response.data["results"]
        }

    def test_filter_by_creator(self):
        """Return only offers belonging to the requested creator."""
        result_ids = self.get_result_ids({
            "creator_id": self.business.pk,
        })

        self.assertEqual(
            result_ids,
            {self.cheap_offer.pk, self.logo_offer.pk},
        )

    def test_filter_by_minimum_price(self):
        """Filter by the cheapest package rather than any matching package."""
        result_ids = self.get_result_ids({
            "min_price": 100,
        })

        self.assertEqual(
            result_ids,
            {self.expensive_offer.pk, self.logo_offer.pk},
        )

    def test_filter_by_maximum_delivery_time(self):
        """Include offers whose shortest delivery time meets the upper limit."""
        result_ids = self.get_result_ids({
            "max_delivery_time": 5,
        })

        self.assertEqual(
            result_ids,
            {self.cheap_offer.pk, self.logo_offer.pk},
        )

    def test_search_matches_title_or_description(self):
        """Search titles and descriptions without matching case."""
        result_ids = self.get_result_ids({
            "search": "WEBSITE",
        })

        self.assertEqual(
            result_ids,
            {self.cheap_offer.pk, self.expensive_offer.pk},
        )

    def test_filters_are_combined(self):
        """Apply creator, price, delivery, and search conditions together."""
        result_ids = self.get_result_ids({
            "creator_id": self.business.pk,
            "min_price": 100,
            "max_delivery_time": 5,
            "search": "logo",
        })

        self.assertEqual(result_ids, {self.logo_offer.pk})

    def test_no_matches_return_empty_results(self):
        """Return an empty paginated result when no offer matches."""
        response = self.client.get(
            self.url,
            {"search": "nonexistent-service"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["results"], [])
        self.assertIsNone(response.data["next"])
        self.assertIsNone(response.data["previous"])

    def test_list_contains_minima_and_nested_data(self):
        """Return calculated minima, creator information, and detail links."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        result = next(
            offer
            for offer in response.data["results"]
            if offer["id"] == self.cheap_offer.pk
        )

        self.assertEqual(result["min_price"], 50)
        self.assertEqual(result["min_delivery_time"], 3)
        self.assertEqual(result["user"], self.business.pk)
        self.assertEqual(
            result["user_details"]["username"],
            self.business.username,
        )
        self.assertEqual(len(result["details"]), 3)

        expected_ids = set(
            self.cheap_offer.details.values_list("pk", flat=True)
        )
        self.assertEqual(
            {detail["id"] for detail in result["details"]},
            expected_ids,
        )

        for detail in result["details"]:
            self.assertEqual(
                detail["url"],
                f"/offerdetails/{detail['id']}/",
            )