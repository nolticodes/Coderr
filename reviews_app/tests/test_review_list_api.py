from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from reviews_app.models import Reviews

from .helpers import (
    authenticate,
    create_review,
    create_review_users,
)


class ReviewListApiTests(APITestCase):
    """Test review list access, filtering, sorting, and response fields."""

    def setUp(self):
        """Create reviews with distinct authors, providers, ratings, and dates."""
        self.url = "/api/reviews/"
        self.users = create_review_users()

        self.first = create_review(
            self.users["business"],
            self.users["customer"],
            rating=2,
        )
        self.second = create_review(
            self.users["business"],
            self.users["othercustomer"],
            rating=5,
        )
        self.third = create_review(
            self.users["otherbusiness"],
            self.users["customer"],
            rating=3,
        )

        now = timezone.now()

        for review, days_ago in [
            (self.first, 3),
            (self.second, 2),
            (self.third, 1),
        ]:
            Reviews.objects.filter(pk=review.pk).update(
                updated_at=now - timedelta(days=days_ago)
            )

        authenticate(self.client, self.users["customer"])

    def get_results(self, response):
        """Extract results with or without global pagination."""
        if isinstance(response.data, dict):
            return response.data["results"]

        return response.data

    def test_authenticated_user_can_list_reviews(self):
        """Return reviews with participant IDs and the expected response fields."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self.get_results(response)

        self.assertEqual(
            {review["id"] for review in results},
            {self.first.pk, self.second.pk, self.third.pk},
        )

        review = next(
            item for item in results
            if item["id"] == self.first.pk
        )

        self.assertEqual(
            set(review),
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
            review["business_user"],
            self.users["business"].pk,
        )
        self.assertEqual(
            review["reviewer"],
            self.users["customer"].pk,
        )

    def test_business_user_can_list_reviews(self):
        """Allow authenticated business users to read the review list."""
        authenticate(self.client, self.users["business"])

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_user_cannot_list_reviews(self):
        """Reject review listing without authentication."""
        self.client.credentials()

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_filter_by_business_user(self):
        """Return only reviews for the requested business user."""
        response = self.client.get(
            self.url,
            {"business_user_id": self.users["business"].pk},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {item["id"] for item in self.get_results(response)},
            {self.first.pk, self.second.pk},
        )

    def test_filter_by_reviewer(self):
        """Return only reviews written by the requested user."""
        response = self.client.get(
            self.url,
            {"reviewer_id": self.users["customer"].pk},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {item["id"] for item in self.get_results(response)},
            {self.first.pk, self.third.pk},
        )

    def test_filters_are_combined(self):
        """Apply provider and reviewer filters together."""
        response = self.client.get(
            self.url,
            {
                "business_user_id": self.users["business"].pk,
                "reviewer_id": self.users["customer"].pk,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["id"] for item in self.get_results(response)],
            [self.first.pk],
        )

    def test_supported_orderings(self):
        """Apply ascending and descending rating and modification-date ordering."""
        cases = [
            ("rating", [self.first.pk, self.third.pk, self.second.pk]),
            ("-rating", [self.second.pk, self.third.pk, self.first.pk]),
            ("updated_at", [self.first.pk, self.second.pk, self.third.pk]),
            ("-updated_at", [self.third.pk, self.second.pk, self.first.pk]),
        ]

        for ordering, expected_ids in cases:
            with self.subTest(ordering=ordering):
                response = self.client.get(
                    self.url,
                    {"ordering": ordering},
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_200_OK,
                )
                self.assertEqual(
                    [
                        item["id"]
                        for item in self.get_results(response)
                    ],
                    expected_ids,
                )

    def test_filter_and_ordering_work_together(self):
        """Sort the filtered reviews without including unrelated providers."""
        response = self.client.get(
            self.url,
            {
                "business_user_id": self.users["business"].pk,
                "ordering": "-rating",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["id"] for item in self.get_results(response)],
            [self.second.pk, self.first.pk],
        )

    def test_no_matches_return_empty_results(self):
        """Return no reviews when the combined filters have no match."""
        response = self.client.get(
            self.url,
            {
                "business_user_id": self.users["otherbusiness"].pk,
                "reviewer_id": self.users["othercustomer"].pk,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.get_results(response), [])