from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import User
from reviews_app.models import Reviews

from .helpers import authenticate, create_review_users


class ReviewCreateApiTests(APITestCase):
    """Test review creation, input validation, and author assignment."""

    def setUp(self):
        """Create participants and authenticate a customer."""
        self.url = "/api/reviews/"
        self.users = create_review_users()
        self.data = {
            "business_user": self.users["business"].pk,
            "rating": 4,
            "description": "Very professional service.",
        }

        authenticate(self.client, self.users["customer"])

    def test_customer_can_create_review(self):
        """Create a review attributed to the authenticated customer."""
        response = self.client.post(
            self.url,
            self.data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(Reviews.objects.count(), 1)

        review = Reviews.objects.get(pk=response.data["id"])

        self.assertEqual(
            review.reviewer_id,
            self.users["customer"].pk,
        )
        self.assertEqual(
            review.business_user_id,
            self.users["business"].pk,
        )
        self.assertEqual(review.rating, 4)
        self.assertEqual(
            review.description,
            self.data["description"],
        )

        self.assertEqual(
            set(response.data),
            {
                "id",
                "business_user",
                "reviewer",
                "rating",
                "description",
                "created_at",
                "updated_at",
            },
        )
        self.assertEqual(
            response.data["reviewer"],
            self.users["customer"].pk,
        )
        self.assertEqual(
            response.data["business_user"],
            self.users["business"].pk,
        )
        self.assertEqual(response.data["rating"], 4)
        self.assertEqual(
            response.data["description"],
            self.data["description"],
        )
        self.assertTrue(response.data["created_at"])
        self.assertTrue(response.data["updated_at"])

    def test_request_cannot_override_reviewer(self):
        """Ignore a supplied reviewer and use the authenticated user."""
        data = {
            **self.data,
            "reviewer": self.users["othercustomer"].pk,
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        review = Reviews.objects.get(pk=response.data["id"])
        self.assertEqual(
            review.reviewer_id,
            self.users["customer"].pk,
        )

    def test_business_user_cannot_create_review(self):
        """Reject review creation by business users."""
        authenticate(self.client, self.users["business"])

        response = self.client.post(
            self.url,
            self.data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(Reviews.objects.count(), 0)

    def test_anonymous_user_cannot_create_review(self):
        """Reject review creation without authentication."""
        self.client.credentials()

        response = self.client.post(
            self.url,
            self.data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertEqual(Reviews.objects.count(), 0)

    def test_missing_required_fields_are_rejected(self):
        """Require the business user, rating, and description."""
        for field in ["business_user", "rating", "description"]:
            with self.subTest(field=field):
                data = self.data.copy()
                data.pop(field)

                response = self.client.post(
                    self.url,
                    data,
                    format="json",
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_400_BAD_REQUEST,
                )
                self.assertIn(field, response.data)

        self.assertEqual(Reviews.objects.count(), 0)

    def test_invalid_ratings_are_rejected(self):
        """Reject ratings outside the choices and empty or malformed values."""
        for rating in [0, 6, "invalid", None, ""]:
            with self.subTest(rating=rating):
                data = {**self.data, "rating": rating}

                response = self.client.post(
                    self.url,
                    data,
                    format="json",
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_400_BAD_REQUEST,
                )
                self.assertIn("rating", response.data)

        self.assertEqual(Reviews.objects.count(), 0)

    def test_rating_boundaries_are_accepted(self):
        """Accept the lowest and highest allowed rating."""
        for rating in [1, 5]:
            with self.subTest(rating=rating):
                data = {**self.data, "rating": rating}

                response = self.client.post(
                    self.url,
                    data,
                    format="json",
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_201_CREATED,
                )
                self.assertEqual(response.data["rating"], rating)

                # Keep each boundary case independent of duplicate-review rules.
                Reviews.objects.get(pk=response.data["id"]).delete()

    def test_unknown_business_user_is_rejected(self):
        """Reject a foreign key pointing to a user who does not exist."""
        missing_id = User.objects.order_by("-pk").first().pk + 1
        data = {**self.data, "business_user": missing_id}

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("business_user", response.data)
        self.assertEqual(Reviews.objects.count(), 0)

    def test_invalid_descriptions_are_rejected(self):
        """Reject empty descriptions and text exceeding the model limit."""
        max_length = Reviews._meta.get_field(
            "description"
        ).max_length

        for description in ["", "x" * (max_length + 1)]:
            with self.subTest(description=description):
                data = {
                    **self.data,
                    "description": description,
                }

                response = self.client.post(
                    self.url,
                    data,
                    format="json",
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_400_BAD_REQUEST,
                )
                self.assertIn("description", response.data)

        self.assertEqual(Reviews.objects.count(), 0)