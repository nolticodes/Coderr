from copy import deepcopy

from django.test import TestCase

from offers_app.models import Offer, OfferDetail
from offers_app.api.serializers import PostNewOfferRequestSerializer

from .helpers import build_offer_data, create_business_user


class OfferCreateSerializerTests(TestCase):
    """Test nested offer creation and package revision defaults."""

    def setUp(self):
        """Create a provider and fresh offer input."""
        self.user = create_business_user()
        self.data = build_offer_data()

    def test_create_offer_with_nested_details(self):
        """Create an offer and correctly associate its three packages."""
        serializer = PostNewOfferRequestSerializer(data=self.data)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        offer = serializer.save(user=self.user)

        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(offer.user_id, self.user.id)
        self.assertEqual(offer.title, self.data["title"])
        self.assertEqual(offer.details.count(), 3)

        for expected in self.data["details"]:
            detail = offer.details.get(
                offer_type=expected["offer_type"]
            )

            self.assertEqual(detail.title, expected["title"])
            self.assertEqual(detail.price, expected["price"])
            self.assertEqual(detail.features, expected["features"])
            self.assertEqual(
                detail.delivery_time,
                expected["delivery_time_in_days"],
            )

    def test_missing_revisions_receive_type_defaults(self):
        """Apply the correct revision default to each package type."""
        serializer = PostNewOfferRequestSerializer(data=self.data)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        offer = serializer.save(user=self.user)

        for offer_type, expected in {
            "basic": 2,
            "standard": 5,
            "premium": 10,
        }.items():
            with self.subTest(offer_type=offer_type):
                detail = offer.details.get(offer_type=offer_type)

                self.assertEqual(detail.revisions, expected)

    def test_explicit_revisions_override_defaults(self):
        """Preserve supplied revisions, including zero, and default missing values."""
        self.data["details"][0]["revisions"] = 0
        self.data["details"][1]["revisions"] = 8

        serializer = PostNewOfferRequestSerializer(data=self.data)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        offer = serializer.save(user=self.user)

        self.assertEqual(
            offer.details.get(offer_type="basic").revisions,
            0,
        )
        self.assertEqual(
            offer.details.get(offer_type="standard").revisions,
            8,
        )
        self.assertEqual(
            offer.details.get(offer_type="premium").revisions,
            10,
        )

    def test_creation_requires_exactly_three_details(self):
        """Reject package lists containing fewer or more than three entries."""
        for count in [0, 1, 2, 4]:
            with self.subTest(count=count):
                data = build_offer_data()
                data["details"] = [
                    deepcopy(self.data["details"][index % 3])
                    for index in range(count)
                ]

                serializer = PostNewOfferRequestSerializer(data=data)

                self.assertFalse(serializer.is_valid())
                self.assertIn("details", serializer.errors)

        self.assertEqual(Offer.objects.count(), 0)
        self.assertEqual(OfferDetail.objects.count(), 0)