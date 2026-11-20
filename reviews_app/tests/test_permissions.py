from types import SimpleNamespace

from django.contrib.auth.models import AnonymousUser
from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from reviews_app.api.permissions import (
    IsCustomerAndIsAuthenticated,
    IsOwner,
)


class ReviewPermissionTests(SimpleTestCase):
    """Test review permissions for authentication, user roles, and authorship."""

    def setUp(self):
        """Create request tools and lightweight user and review objects."""
        self.factory = APIRequestFactory()

        self.customer = SimpleNamespace(
            id=1,
            type="customer",
            is_authenticated=True,
        )
        self.other_customer = SimpleNamespace(
            id=2,
            type="customer",
            is_authenticated=True,
        )
        self.business = SimpleNamespace(
            id=3,
            type="business",
            is_authenticated=True,
        )
        self.review = SimpleNamespace(
            reviewer_id=self.customer.id,
        )

    def build_request(self, method, user):
        """Build a request with the supplied method and user."""
        request = self.factory.generic(
            method,
            "/api/reviews/",
        )
        request.user = user
        return request

    def test_customer_permission_rejects_anonymous_users(self):
        """Reject unauthenticated requests for safe and unsafe methods."""
        permission = IsCustomerAndIsAuthenticated()

        for method in ["GET", "HEAD", "OPTIONS", "POST", "PATCH", "DELETE"]:
            with self.subTest(method=method):
                request = self.build_request(
                    method,
                    AnonymousUser(),
                )

                self.assertFalse(
                    permission.has_permission(request, view=None)
                )

    def test_authenticated_users_can_read(self):
        """Allow customer and business users through safe-method checks."""
        permission = IsCustomerAndIsAuthenticated()

        for user in [self.customer, self.business]:
            for method in ["GET", "HEAD", "OPTIONS"]:
                with self.subTest(user_type=user.type, method=method):
                    request = self.build_request(method, user)

                    self.assertTrue(
                        permission.has_permission(request, view=None)
                    )

    def test_customers_can_write(self):
        """Allow authenticated customers through unsafe-method checks."""
        permission = IsCustomerAndIsAuthenticated()

        for method in ["POST", "PUT", "PATCH", "DELETE"]:
            with self.subTest(method=method):
                request = self.build_request(method, self.customer)

                self.assertTrue(
                    permission.has_permission(request, view=None)
                )

    def test_business_users_cannot_write(self):
        """Reject business users through customer-only write checks."""
        permission = IsCustomerAndIsAuthenticated()

        for method in ["POST", "PUT", "PATCH", "DELETE"]:
            with self.subTest(method=method):
                request = self.build_request(method, self.business)

                self.assertFalse(
                    permission.has_permission(request, view=None)
                )

    def test_owner_permission_requires_authentication(self):
        """Reject anonymous users before checking review ownership."""
        permission = IsOwner()
        request = self.build_request("PATCH", AnonymousUser())

        self.assertFalse(
            permission.has_permission(request, view=None)
        )

    def test_owner_permission_accepts_authenticated_users(self):
        """Allow authenticated users to proceed to the object check."""
        permission = IsOwner()

        for user in [self.customer, self.other_customer, self.business]:
            with self.subTest(user_id=user.id):
                request = self.build_request("PATCH", user)

                self.assertTrue(
                    permission.has_permission(request, view=None)
                )

    def test_review_author_passes_object_permission(self):
        """Allow the review author to access their review."""
        permission = IsOwner()

        for method in ["GET", "PATCH", "DELETE"]:
            with self.subTest(method=method):
                request = self.build_request(method, self.customer)

                self.assertTrue(
                    permission.has_object_permission(
                        request,
                        view=None,
                        obj=self.review,
                    )
                )

    def test_other_users_fail_object_permission(self):
        """Reject access by non-authors, including safe-method access."""
        permission = IsOwner()

        for user in [self.other_customer, self.business]:
            for method in ["GET", "PATCH", "DELETE"]:
                with self.subTest(user_id=user.id, method=method):
                    request = self.build_request(method, user)

                    self.assertFalse(
                        permission.has_object_permission(
                            request,
                            view=None,
                            obj=self.review,
                        )
                    )