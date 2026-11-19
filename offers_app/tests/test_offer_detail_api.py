from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail

from .helpers import create_business_user, create_offer


class OfferDetailApiTests(APITestCase):
    """Test offer retrieval, nested PATCH responses, and missing resources."""

    def setUp(self):
        """Create an offer and authenticate its owner."""
        self.user = create_business_user()
        self.offer = create_offer(self.user)
        self.url = f"/api/offers/{self.offer.pk}/"

        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

    def test_retrieve_offer(self):
        """Return the selected offer with its creator ID and detail links."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data),
            {
                "id",
                "user",
                "title",
                "image",
                "description",
                "created_at",
                "updated_at",
                "details",
            },
        )
        self.assertEqual(response.data["id"], self.offer.pk)
        self.assertEqual(response.data["user"], self.user.pk)
        self.assertEqual(len(response.data["details"]), 3)

        for detail in response.data["details"]:
            self.assertEqual(set(detail), {"id", "url"})

    def test_patch_returns_updated_offer_and_all_packages(self):
        """Return current package data after updating one nested package."""
        basic = self.offer.details.get(offer_type="basic")
        original_ids = set(
            self.offer.details.values_list("pk", flat=True)
        )

        response = self.client.patch(
            self.url,
            {
                "title": "Updated design offer",
                "details": [
                    {
                        "offer_type": "basic",
                        "price": 175,
                    }
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["title"],
            "Updated design offer",
        )
        self.assertEqual(len(response.data["details"]), 3)
        self.assertEqual(
            {detail["id"] for detail in response.data["details"]},
            original_ids,
        )

        returned_basic = next(
            detail
            for detail in response.data["details"]
            if detail["offer_type"] == "basic"
        )

        self.assertEqual(returned_basic["id"], basic.pk)
        self.assertEqual(returned_basic["price"], 175)

        basic.refresh_from_db()
        self.offer.refresh_from_db()

        self.assertEqual(basic.price, 175)
        self.assertEqual(self.offer.title, "Updated design offer")

    def test_patch_without_package_type_returns_bad_request(self):
        """Reject an unidentified package update without changing stored values."""
        basic = self.offer.details.get(offer_type="basic")

        response = self.client.patch(
            self.url,
            {"details": [{"price": 175}]},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("details", response.data)

        basic.refresh_from_db()
        self.assertEqual(basic.price, 100)

    def test_missing_offer_returns_not_found(self):
        """Return 404 for retrieval, update, or deletion of an unknown offer."""
        missing_id = self.offer.pk + 1000
        url = f"/api/offers/{missing_id}/"

        requests = [
            ("GET", lambda: self.client.get(url)),
            (
                "PATCH",
                lambda: self.client.patch(
                    url,
                    {"title": "Updated"},
                    format="json",
                ),
            ),
            ("DELETE", lambda: self.client.delete(url)),
        ]

        for method, send_request in requests:
            with self.subTest(method=method):
                response = send_request()

                self.assertEqual(
                    response.status_code,
                    status.HTTP_404_NOT_FOUND,
                )


class SpecificOfferDetailApiTests(APITestCase):
    """Test authenticated retrieval of individual offer packages."""

    def setUp(self):
        """Create a package and authenticate its provider."""
        self.user = create_business_user()
        offer = create_offer(self.user)
        self.detail = offer.details.get(offer_type="basic")
        self.url = f"/api/offerdetails/{self.detail.pk}/"

        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

    def test_retrieve_specific_package(self):
        """Return the selected package with its full fields."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data),
            {
                "id",
                "title",
                "revisions",
                "delivery_time_in_days",
                "price",
                "features",
                "offer_type",
            },
        )
        self.assertEqual(response.data["id"], self.detail.pk)
        self.assertEqual(response.data["offer_type"], "basic")
        self.assertEqual(
            response.data["delivery_time_in_days"],
            self.detail.delivery_time,
        )
        self.assertEqual(response.data["price"], self.detail.price)

    def test_missing_package_returns_not_found(self):
        """Return 404 when the requested package does not exist."""
        missing_id = (
            OfferDetail.objects.order_by("-pk")
            .values_list("pk", flat=True)
            .first()
        ) + 1

        response = self.client.get(
            f"/api/offerdetails/{missing_id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_anonymous_access_is_rejected(self):
        """Reject package retrieval without authentication."""
        self.client.credentials()

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )