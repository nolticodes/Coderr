from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import User
from profile_app.models import Profile

from .helpers import create_user_with_profile


class ProfileDetailApiTests(APITestCase):
    """Test profile retrieval, owner updates, and endpoint restrictions."""

    def setUp(self):
        """Create a profile whose primary key differs from its user's ID."""
        User.objects.create_user(
            username="userwithoutprofile",
            email="withoutprofile@example.com",
            password="Testpasswort123!",
            type="customer",
        )

        self.owner, self.profile = create_user_with_profile(
            "profileowner"
        )
        self.other_user, _ = create_user_with_profile(
            "othercustomer"
        )

        self.url = f"/api/profile/{self.owner.pk}/"

    def authenticate(self, user):
        """Authenticate subsequent requests using the user's token."""
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

    def test_retrieve_profile_by_user_id(self):
        """Use the user ID from the URL rather than the profile primary key."""
        self.authenticate(self.owner)

        self.assertNotEqual(self.profile.pk, self.owner.pk)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"], self.owner.pk)
        self.assertEqual(
            response.data["username"],
            self.owner.username,
        )
        self.assertEqual(response.data["email"], self.owner.email)
        self.assertEqual(response.data["type"], self.owner.type)
        self.assertEqual(response.data["first_name"], "Max")
        self.assertEqual(response.data["location"], "Berlin")
        self.assertTrue(response.data["created_at"])

    def test_authenticated_user_can_read_another_profile(self):
        """Allow authenticated users to retrieve profiles they do not own."""
        self.authenticate(self.other_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"], self.owner.pk)

    def test_anonymous_user_cannot_retrieve_profile(self):
        """Reject profile retrieval without authentication."""
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_owner_can_update_profile_and_email(self):
        """Save profile and user changes and return the full updated profile."""
        self.authenticate(self.owner)

        response = self.client.patch(
            self.url,
            {
                "first_name": "Erika",
                "location": "Hamburg",
                "email": "updated@example.com",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.profile.refresh_from_db()
        self.owner.refresh_from_db()

        self.assertEqual(self.profile.first_name, "Erika")
        self.assertEqual(self.profile.location, "Hamburg")
        self.assertEqual(self.owner.email, "updated@example.com")

        self.assertEqual(
            set(response.data),
            {
                "user",
                "username",
                "first_name",
                "last_name",
                "file",
                "location",
                "tel",
                "description",
                "working_hours",
                "type",
                "email",
                "created_at",
            },
        )
        self.assertEqual(response.data["first_name"], "Erika")
        self.assertEqual(response.data["location"], "Hamburg")
        self.assertEqual(
            response.data["email"],
            "updated@example.com",
        )
        self.assertEqual(response.data["last_name"], "Mustermann")
        self.assertEqual(response.data["user"], self.owner.pk)

    def test_owner_can_update_without_sending_email(self):
        """Allow a partial profile update without requiring the email field."""
        self.authenticate(self.owner)

        response = self.client.patch(
            self.url,
            {"location": "Hamburg"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.profile.refresh_from_db()
        self.owner.refresh_from_db()

        self.assertEqual(self.profile.location, "Hamburg")
        self.assertEqual(
            self.owner.email,
            "profileowner@example.com",
        )

    def test_other_user_cannot_update_profile(self):
        """Reject non-owner changes and preserve both profile and user data."""
        self.authenticate(self.other_user)

        response = self.client.patch(
            self.url,
            {
                "location": "Hamburg",
                "email": "unauthorized@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.profile.refresh_from_db()
        self.owner.refresh_from_db()

        self.assertEqual(self.profile.location, "Berlin")
        self.assertEqual(
            self.owner.email,
            "profileowner@example.com",
        )

    def test_anonymous_user_cannot_update_profile(self):
        """Reject anonymous changes and preserve the profile."""
        response = self.client.patch(
            self.url,
            {"location": "Hamburg"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.location, "Berlin")

    def test_invalid_email_returns_bad_request(self):
        """Reject invalid input before saving any requested changes."""
        self.authenticate(self.owner)

        response = self.client.patch(
            self.url,
            {
                "email": "invalid-email",
                "location": "Hamburg",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("email", response.data)

        self.profile.refresh_from_db()
        self.owner.refresh_from_db()

        self.assertEqual(self.profile.location, "Berlin")
        self.assertEqual(
            self.owner.email,
            "profileowner@example.com",
        )

    def test_missing_profile_returns_not_found(self):
        """Return 404 when a user exists but has no associated profile."""
        self.authenticate(self.owner)
        user = User.objects.get(username="userwithoutprofile")
        url = f"/api/profile/{user.pk}/"

        get_response = self.client.get(url)
        patch_response = self.client.patch(
            url,
            {"location": "Hamburg"},
            format="json",
        )

        self.assertEqual(
            get_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(
            patch_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_unsupported_methods_are_rejected(self):
        """Reject POST, PUT, and DELETE even when called by the owner."""
        self.authenticate(self.owner)

        for method in ["post", "put", "delete"]:
            with self.subTest(method=method):
                response = getattr(self.client, method)(
                    self.url,
                    {},
                    format="json",
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_405_METHOD_NOT_ALLOWED,
                )

        self.assertTrue(
            Profile.objects.filter(pk=self.profile.pk).exists()
        )