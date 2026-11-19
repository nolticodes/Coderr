from copy import deepcopy

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import User
from offers_app.models import Offer, OfferDetail


class OfferPermissionTests(APITestCase):
    """Test offer access for anonymous users, customers, owners, and other providers."""

    def setUp(self):
        """Create users, an existing offer, and valid offer creation data."""
        self.list_url = "/api/offers/"

        self.owner = User.objects.create_user(
            username="offerowner",
            email="owner@example.com",
            password="Testpasswort123!",
            type="business",
        )
        self.other_business = User.objects.create_user(
            username="otherbusiness",
            email="other@example.com",
            password="Testpasswort123!",
            type="business",
        )
        self.customer = User.objects.create_user(
            username="testcustomer",
            email="customer@example.com",
            password="Testpasswort123!",
            type="customer",
        )

        self.offer = Offer.objects.create(
            user=self.owner,
            title="Original offer",
            image=None,
            description="Original description",
        )
        self.detail_url = f"/api/offers/{self.offer.pk}/"

        packages = [
            ("basic", 100, 5, 2),
            ("standard", 200, 7, 5),
            ("premium", 300, 10, 10),
        ]

        self.offer_data = {
            "title": "New offer",
            "image": None,
            "description": "New offer description",
            "details": [],
        }

        for offer_type, price, delivery_time, revisions in packages:
            OfferDetail.objects.create(
                offer=self.offer,
                title=f"{offer_type.title()} package",
                revisions=revisions,
                price=price,
                delivery_time=delivery_time,
                features=["Logo design"],
                offer_type=offer_type,
            )

            self.offer_data["details"].append({
                "title": f"{offer_type.title()} package",
                "revisions": revisions,
                "delivery_time_in_days": delivery_time,
                "price": price,
                "features": ["Logo design"],
                "offer_type": offer_type,
            })

    def authenticate(self, user):
        """Authenticate subsequent requests using the user's token."""
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

    def test_anonymous_user_can_list_offers(self):
        """Allow public access to the offer list."""
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_user_cannot_create_offer(self):
        """Reject anonymous creation without saving an offer or its details."""
        offer_count = Offer.objects.count()
        detail_count = OfferDetail.objects.count()

        response = self.client.post(
            self.list_url,
            deepcopy(self.offer_data),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertEqual(Offer.objects.count(), offer_count)
        self.assertEqual(OfferDetail.objects.count(), detail_count)

    def test_customer_cannot_create_offer(self):
        """Reject offer creation by an authenticated customer."""
        self.authenticate(self.customer)
        offer_count = Offer.objects.count()
        detail_count = OfferDetail.objects.count()

        response = self.client.post(
            self.list_url,
            deepcopy(self.offer_data),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(Offer.objects.count(), offer_count)
        self.assertEqual(OfferDetail.objects.count(), detail_count)

    def test_business_user_can_create_offer(self):
        """Allow a business user to create an offer assigned to their account."""
        self.authenticate(self.other_business)
        offer_count = Offer.objects.count()

        response = self.client.post(
            self.list_url,
            deepcopy(self.offer_data),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(Offer.objects.count(), offer_count + 1)

        offer = Offer.objects.get(pk=response.data["id"])

        self.assertEqual(offer.user_id, self.other_business.id)
        self.assertEqual(offer.details.count(), 3)

    def test_anonymous_user_cannot_retrieve_offer(self):
        """Reject anonymous access to an individual offer."""
        response = self.client.get(self.detail_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_users_can_retrieve_foreign_offer(self):
        """Allow customers and other providers to read an existing offer."""
        for user in [self.customer, self.other_business]:
            with self.subTest(user_type=user.type):
                self.authenticate(user)

                response = self.client.get(self.detail_url)

                self.assertEqual(
                    response.status_code,
                    status.HTTP_200_OK,
                )
                self.assertEqual(response.data["id"], self.offer.pk)

    def test_owner_can_update_offer(self):
        """Allow the owner to update their offer."""
        self.authenticate(self.owner)

        response = self.client.patch(
            self.detail_url,
            {"title": "Updated offer"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.offer.refresh_from_db()
        self.assertEqual(self.offer.title, "Updated offer")

    def test_non_owners_cannot_update_offer(self):
        """Reject updates by customers and providers who do not own the offer."""
        for user in [self.customer, self.other_business]:
            with self.subTest(user_type=user.type):
                self.authenticate(user)

                response = self.client.patch(
                    self.detail_url,
                    {"title": "Unauthorized change"},
                    format="json",
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_403_FORBIDDEN,
                )

                self.offer.refresh_from_db()
                self.assertEqual(self.offer.title, "Original offer")

    def test_anonymous_user_cannot_update_offer(self):
        """Reject anonymous updates and preserve the original offer."""
        response = self.client.patch(
            self.detail_url,
            {"title": "Unauthorized change"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.offer.refresh_from_db()
        self.assertEqual(self.offer.title, "Original offer")

    def test_owner_can_delete_offer(self):
        """Allow the owner to delete their offer and its associated details."""
        self.authenticate(self.owner)
        offer_id = self.offer.pk
        detail_ids = list(
            self.offer.details.values_list("pk", flat=True)
        )

        response = self.client.delete(self.detail_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(
            Offer.objects.filter(pk=offer_id).exists()
        )
        self.assertFalse(
            OfferDetail.objects.filter(pk__in=detail_ids).exists()
        )

    def test_non_owners_cannot_delete_offer(self):
        """Reject deletion by non-owners and preserve the offer and its details."""
        for user in [self.customer, self.other_business]:
            with self.subTest(user_type=user.type):
                self.authenticate(user)

                response = self.client.delete(self.detail_url)

                self.assertEqual(
                    response.status_code,
                    status.HTTP_403_FORBIDDEN,
                )
                self.assertTrue(
                    Offer.objects.filter(pk=self.offer.pk).exists()
                )
                self.assertEqual(self.offer.details.count(), 3)

    def test_anonymous_user_cannot_delete_offer(self):
        """Reject anonymous deletion and preserve the offer and its details."""
        response = self.client.delete(self.detail_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertTrue(
            Offer.objects.filter(pk=self.offer.pk).exists()
        )
        self.assertEqual(self.offer.details.count(), 3)