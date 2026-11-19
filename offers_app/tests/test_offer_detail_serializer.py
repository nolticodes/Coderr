from django.test import TestCase

from offers_app.api.serializers import (
    OfferDetailSerializer,
    OfferStatsSerializer,
)

from .helpers import (
    build_offer_data,
    create_business_user,
    create_offer,
)


class OfferDetailSerializerTests(TestCase):
    """Test package field validation, source mapping, and detail URLs."""

    def test_invalid_package_type_is_rejected(self):
        """Reject a package type outside the model choices."""
        data = build_offer_data()["details"][0]
        data["offer_type"] = "unknown"

        serializer = OfferStatsSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("offer_type", serializer.errors)

    def test_features_must_be_a_list(self):
        """Reject a plain string where a feature list is required."""
        data = build_offer_data()["details"][0]
        data["features"] = "Logo"

        serializer = OfferStatsSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("features", serializer.errors)

    def test_delivery_time_source_mapping(self):
        """Map the API delivery field to the model field during validation."""
        serializer = OfferStatsSerializer(
            data=build_offer_data()["details"][0]
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            serializer.validated_data["delivery_time"],
            5,
        )
        self.assertNotIn(
            "delivery_time_in_days",
            serializer.validated_data,
        )

    def test_detail_url_contains_detail_id(self):
        """Serialize the package ID and its relative detail URL."""
        user = create_business_user()
        offer = create_offer(user)
        detail = offer.details.get(offer_type="basic")

        data = OfferDetailSerializer(detail).data

        self.assertEqual(data["id"], detail.pk)
        self.assertEqual(
            data["url"],
            f"/offerdetails/{detail.pk}/",
        )