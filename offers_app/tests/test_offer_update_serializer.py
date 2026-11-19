from django.test import TestCase
from rest_framework import serializers

from offers_app.models import Offer
from offers_app.api.serializers import (
    OfferStatsSerializer,
    PatchOfferDetailsRequestSerializer,
)

from .helpers import create_business_user, create_offer


class OfferUpdateSerializerTests(TestCase):
    """Test partial offer updates and nested package changes."""

    def setUp(self):
        """Create a provider and an offer with three packages."""
        self.user = create_business_user()
        self.offer = create_offer(self.user)

    def test_partial_update_of_offer_title(self):
        """Update the title without requiring or changing package data."""
        original_details = list(
            self.offer.details.order_by("pk").values()
        )

        serializer = PatchOfferDetailsRequestSerializer(
            self.offer,
            data={"title": "Updated title"},
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        self.offer.refresh_from_db()

        self.assertEqual(self.offer.title, "Updated title")
        self.assertEqual(
            list(self.offer.details.order_by("pk").values()),
            original_details,
        )

    def test_partial_update_changes_only_selected_package_fields(self):
        """Update one package while preserving all unspecified values."""
        basic = self.offer.details.get(offer_type="basic")
        other_details_before = list(
            self.offer.details.exclude(pk=basic.pk)
            .order_by("pk")
            .values()
        )

        serializer = PatchOfferDetailsRequestSerializer(
            self.offer,
            data={
                "details": [
                    {
                        "offer_type": "basic",
                        "price": 150,
                    }
                ]
            },
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        basic.refresh_from_db()

        self.assertEqual(basic.price, 150)
        self.assertEqual(basic.title, "Basic")
        self.assertEqual(basic.revisions, 2)
        self.assertEqual(basic.delivery_time, 5)
        self.assertEqual(basic.features, ["Logo"])
        self.assertEqual(self.offer.details.count(), 3)
        self.assertEqual(
            list(
                self.offer.details.exclude(pk=basic.pk)
                .order_by("pk")
                .values()
            ),
            other_details_before,
        )

    def test_update_without_package_type_is_rejected(self):
        """Reject a package update that does not identify the target type."""
        basic = self.offer.details.get(offer_type="basic")

        serializer = PatchOfferDetailsRequestSerializer(
            self.offer,
            data={"details": [{"price": 150}]},
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        with self.assertRaises(serializers.ValidationError):
            serializer.save()

        basic.refresh_from_db()
        self.assertEqual(basic.price, 100)

    def test_failed_update_rolls_back_previous_package_changes(self):
        """Roll back an earlier package change when a later entry is invalid."""
        serializer = PatchOfferDetailsRequestSerializer(
            self.offer,
            data={
                "details": [
                    {"offer_type": "basic", "price": 150},
                    {"price": 250},
                ]
            },
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        with self.assertRaises(serializers.ValidationError):
            serializer.save()

        basic = self.offer.details.get(offer_type="basic")
        self.assertEqual(basic.price, 100)

    def test_update_clears_prefetched_details(self):
        """Ensure serialization uses current package values after an update."""
        offer = Offer.objects.prefetch_related("details").get(
            pk=self.offer.pk
        )

        serializer = PatchOfferDetailsRequestSerializer(
            offer,
            data={
                "details": [
                    {"offer_type": "basic", "price": 175}
                ]
            },
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_offer = serializer.save()

        details = OfferStatsSerializer(
            updated_offer.details.all(),
            many=True,
        ).data
        basic = next(
            detail
            for detail in details
            if detail["offer_type"] == "basic"
        )

        self.assertEqual(basic["price"], 175)