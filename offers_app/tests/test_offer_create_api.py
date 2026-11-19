from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail

from .helpers import build_offer_data, create_business_user


class OfferCreateApiTests(APITestCase):
    """Test creation responses and rejection of invalid nested requests."""

    def setUp(self):
        """Authenticate a business user and prepare valid offer input."""
        self.url = "/api/offers/"
        self.user = create_business_user()
        self.data = build_offer_data()

        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

    def test_creation_returns_saved_package_details(self):
        """Return the created offer and full nested packages with generated IDs."""
        response = self.client.post(
            self.url,
            self.data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            set(response.data),
            {"id", "title", "image", "description", "details"},
        )

        offer = Offer.objects.get(pk=response.data["id"])

        self.assertEqual(offer.user_id, self.user.pk)
        self.assertEqual(response.data["title"], self.data["title"])
        self.assertEqual(response.data["description"], self.data["description"])
        self.assertIsNone(response.data["image"])
        self.assertEqual(len(response.data["details"]), 3)

        expected_revisions = {
            "basic": 2,
            "standard": 5,
            "premium": 10,
        }

        for returned_detail in response.data["details"]:
            detail = OfferDetail.objects.get(
                pk=returned_detail["id"]
            )

            self.assertEqual(detail.offer_id, offer.pk)
            self.assertEqual(
                returned_detail["revisions"],
                expected_revisions[detail.offer_type],
            )
            self.assertEqual(
                returned_detail["delivery_time_in_days"],
                detail.delivery_time,
            )
            self.assertEqual(returned_detail["price"], detail.price)
            self.assertEqual(returned_detail["features"], detail.features)

    def test_invalid_detail_count_returns_bad_request(self):
        """Reject an invalid detail count without saving any offer data."""
        self.data["details"].pop()

        response = self.client.post(
            self.url,
            self.data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("details", response.data)
        self.assertEqual(Offer.objects.count(), 0)
        self.assertEqual(OfferDetail.objects.count(), 0)

    def test_invalid_nested_value_returns_bad_request(self):
        """Reject invalid package input before creating the offer."""
        self.data["details"][0]["price"] = "not-a-number"

        response = self.client.post(
            self.url,
            self.data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("details", response.data)
        self.assertEqual(Offer.objects.count(), 0)
        self.assertEqual(OfferDetail.objects.count(), 0)