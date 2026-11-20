from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import User
from offers_app.models import Offer
from reviews_app.models import Reviews


class BaseInfoApiTests(APITestCase):
    """Test platform counts, average ratings, and public endpoint access."""

    def setUp(self):
        """Define the URL for the platform statistics endpoint."""
        self.url = "/api/base-info/"

    def create_user(self, username, user_type):
        """Create a user with the specified account type."""
        return User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="Testpasswort123!",
            type=user_type,
        )

    def test_empty_platform_returns_zero_values(self):
        """Return zero counts and a zero average when no data exists."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "review_count": 0,
                "average_rating": 0.0,
                "business_profile_count": 0,
                "offer_count": 0,
            },
        )

    def test_platform_statistics(self):
        """Count all reviews and offers while counting only business users."""
        business = self.create_user("business", "business")
        self.create_user("otherbusiness", "business")
        customer = self.create_user("customer", "customer")
        other_customer = self.create_user(
            "othercustomer",
            "customer",
        )

        Offer.objects.create(
            user=business,
            title="First offer",
            description="First description.",
            image=None,
        )
        Offer.objects.create(
            user=business,
            title="Second offer",
            description="Second description.",
            image=None,
        )

        Reviews.objects.create(
            business_user=business,
            reviewer=customer,
            rating=4,
            description="Good service.",
        )
        Reviews.objects.create(
            business_user=business,
            reviewer=other_customer,
            rating=5,
            description="Excellent service.",
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "review_count": 2,
                "average_rating": 4.5,
                "business_profile_count": 2,
                "offer_count": 2,
            },
        )

    def test_average_rating_is_rounded_to_one_decimal_place(self):
        """Round the average of all review ratings to one decimal place."""
        business = self.create_user("business", "business")

        for index, rating in enumerate([4, 5, 5]):
            customer = self.create_user(
                f"customer{index}",
                "customer",
            )
            Reviews.objects.create(
                business_user=business,
                reviewer=customer,
                rating=rating,
                description="Review for rounding.",
            )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["review_count"], 3)
        self.assertEqual(response.data["average_rating"], 4.7)

    def test_users_and_offers_without_reviews(self):
        """Return existing counts and a zero average when reviews are absent."""
        business = self.create_user("business", "business")
        self.create_user("customer", "customer")

        Offer.objects.create(
            user=business,
            title="Design offer",
            description="Professional design.",
            image=None,
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "review_count": 0,
                "average_rating": 0.0,
                "business_profile_count": 1,
                "offer_count": 1,
            },
        )

    def test_post_is_not_allowed(self):
        """Reject attempts to submit data to the read-only statistics endpoint."""
        response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )