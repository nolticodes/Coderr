from types import SimpleNamespace

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from profile_app.api.permissions import IsOwnerOrReadOnly


class IsOwnerOrReadOnlyTests(SimpleTestCase):
    """Test profile object permissions for owners and other users."""

    def setUp(self):
        """Create a permission instance and lightweight profile participants."""
        self.factory = APIRequestFactory()
        self.permission = IsOwnerOrReadOnly()

        self.owner = SimpleNamespace(id=1)
        self.other_user = SimpleNamespace(id=2)
        self.profile = SimpleNamespace(user=self.owner)

    def has_access(self, method, user):
        """Evaluate object access for the supplied method and user."""
        request = self.factory.generic(
            method,
            "/api/profile/1/",
        )
        request.user = user

        return self.permission.has_object_permission(
            request,
            view=None,
            obj=self.profile,
        )

    def test_get_is_allowed_for_non_owner(self):
        """Allow another user to read the profile."""
        self.assertTrue(
            self.has_access("GET", self.other_user)
        )

    def test_owner_can_modify_profile(self):
        """Allow the profile owner through write permission checks."""
        for method in ["PATCH", "PUT", "DELETE"]:
            with self.subTest(method=method):
                self.assertTrue(
                    self.has_access(method, self.owner)
                )

    def test_non_owner_cannot_modify_profile(self):
        """Reject write access for a user who does not own the profile."""
        for method in ["PATCH", "PUT", "DELETE"]:
            with self.subTest(method=method):
                self.assertFalse(
                    self.has_access(method, self.other_user)
                )