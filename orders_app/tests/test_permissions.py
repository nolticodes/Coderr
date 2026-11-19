from types import SimpleNamespace

from django.contrib.auth.models import AnonymousUser
from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.views import APIView

from orders_app.api.permissions import (
    IsBusinessAndIsAuthenticated,
    IsCustomerAndIsAuthenticated,
)


class OrderPermissionTests(SimpleTestCase):
    """Test order permissions for authentication, user types, and ownership."""

    def setUp(self):
        """Create request tools and lightweight authenticated user objects."""
        self.factory = APIRequestFactory()
        self.view = APIView()

        self.customer = SimpleNamespace(
            id=1,
            type="customer",
            is_authenticated=True,
        )
        self.business = SimpleNamespace(
            id=2,
            type="business",
            is_authenticated=True,
        )
        self.other_business = SimpleNamespace(
            id=3,
            type="business",
            is_authenticated=True,
        )

    def build_request(self, method, user):
        """Build a DRF request authenticated as the supplied user."""
        request = self.factory.generic(method, "/api/orders/")
        force_authenticate(request, user=user)

        return self.view.initialize_request(request)

    def test_anonymous_users_are_rejected(self):
        """Reject anonymous requests for both permission classes."""
        for permission_class in [
            IsCustomerAndIsAuthenticated,
            IsBusinessAndIsAuthenticated,
        ]:
            for method in ["GET", "HEAD", "OPTIONS", "POST", "PATCH", "DELETE"]:
                with self.subTest(
                    permission=permission_class.__name__,
                    method=method,
                ):
                    request = self.build_request(
                        method,
                        AnonymousUser(),
                    )

                    self.assertFalse(
                        permission_class().has_permission(
                            request,
                            self.view,
                        )
                    )

    def test_authenticated_users_pass_safe_method_checks(self):
        """Allow authenticated users of either type through safe-method checks."""
        for permission_class in [
            IsCustomerAndIsAuthenticated,
            IsBusinessAndIsAuthenticated,
        ]:
            for user in [self.customer, self.business]:
                for method in ["GET", "HEAD", "OPTIONS"]:
                    with self.subTest(
                        permission=permission_class.__name__,
                        user_type=user.type,
                        method=method,
                    ):
                        request = self.build_request(method, user)

                        self.assertTrue(
                            permission_class().has_permission(
                                request,
                                self.view,
                            )
                        )

    def test_customer_permission_allows_customer_writes(self):
        """Allow customer users through unsafe-method permission checks."""
        permission = IsCustomerAndIsAuthenticated()

        for method in ["POST", "PUT", "PATCH", "DELETE"]:
            with self.subTest(method=method):
                request = self.build_request(method, self.customer)

                self.assertTrue(
                    permission.has_permission(request, self.view)
                )

    def test_customer_permission_rejects_business_writes(self):
        """Reject business users through customer-only write checks."""
        permission = IsCustomerAndIsAuthenticated()

        for method in ["POST", "PUT", "PATCH", "DELETE"]:
            with self.subTest(method=method):
                request = self.build_request(method, self.business)

                self.assertFalse(
                    permission.has_permission(request, self.view)
                )

    def test_business_permission_allows_business_writes(self):
        """Allow business users through unsafe-method permission checks."""
        permission = IsBusinessAndIsAuthenticated()

        for method in ["POST", "PUT", "PATCH", "DELETE"]:
            with self.subTest(method=method):
                request = self.build_request(method, self.business)

                self.assertTrue(
                    permission.has_permission(request, self.view)
                )

    def test_business_permission_rejects_customer_writes(self):
        """Reject customers through business-only write checks."""
        permission = IsBusinessAndIsAuthenticated()

        for method in ["POST", "PUT", "PATCH", "DELETE"]:
            with self.subTest(method=method):
                request = self.build_request(method, self.customer)

                self.assertFalse(
                    permission.has_permission(request, self.view)
                )

    def test_assigned_business_user_passes_object_permission(self):
        """Allow object access for the business user assigned to the order."""
        request = self.build_request("PATCH", self.business)
        order = SimpleNamespace(
            business_user_id=self.business.id,
        )

        permission = IsBusinessAndIsAuthenticated()

        self.assertTrue(
            permission.has_object_permission(
                request,
                self.view,
                order,
            )
        )

    def test_other_business_user_fails_object_permission(self):
        """Reject object access for a provider not assigned to the order."""
        request = self.build_request("PATCH", self.other_business)
        order = SimpleNamespace(
            business_user_id=self.business.id,
        )

        permission = IsBusinessAndIsAuthenticated()

        self.assertFalse(
            permission.has_object_permission(
                request,
                self.view,
                order,
            )
        )

    def test_safe_methods_do_not_bypass_object_ownership(self):
        """Require assignment even for safe methods during object checks."""
        permission = IsBusinessAndIsAuthenticated()
        order = SimpleNamespace(
            business_user_id=self.business.id,
        )

        for method in ["GET", "HEAD", "OPTIONS"]:
            with self.subTest(method=method):
                request = self.build_request(
                    method,
                    self.other_business,
                )

                self.assertFalse(
                    permission.has_object_permission(
                        request,
                        self.view,
                        order,
                    )
                )