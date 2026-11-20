from django.test import TestCase

from auth_app.models import User
from profile_app.models import Profile
from profile_app.api.serializers import (
    PatchProfileDetailsRequestSerializer,
)


class ProfileUpdateSerializerTests(TestCase):
    """Test partial profile updates and changes to the linked user's email."""

    def setUp(self):
        """Create a user and a profile with known initial values."""
        self.user = User.objects.create_user(
            username="testcustomer",
            email="customer@example.com",
            password="Testpasswort123!",
            type="customer",
        )
        self.profile = Profile.objects.create(
            user=self.user,
            first_name="Max",
            last_name="Mustermann",
            file="profile.jpg",
            location="Berlin",
            tel="123456789",
            description="Original description",
            working_hours="9-17",
        )

    def test_update_profile_without_email(self):
        """Update profile fields while preserving the linked user's email."""
        serializer = PatchProfileDetailsRequestSerializer(
            self.profile,
            data={
                "location": "Hamburg",
                "description": "Updated description",
            },
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_profile = serializer.save()

        updated_profile.refresh_from_db()
        self.user.refresh_from_db()

        self.assertEqual(updated_profile.pk, self.profile.pk)
        self.assertEqual(updated_profile.location, "Hamburg")
        self.assertEqual(
            updated_profile.description,
            "Updated description",
        )
        self.assertEqual(
            self.user.email,
            "customer@example.com",
        )

    def test_update_email_without_profile_fields(self):
        """Save the email on the linked user and preserve profile values."""
        serializer = PatchProfileDetailsRequestSerializer(
            self.profile,
            data={"email": "new@example.com"},
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        self.user.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(self.user.email, "new@example.com")
        self.assertEqual(self.profile.first_name, "Max")
        self.assertEqual(self.profile.location, "Berlin")
        self.assertEqual(self.profile.user_id, self.user.pk)

    def test_update_email_and_profile_together(self):
        """Save linked user changes and profile changes in the same request."""
        serializer = PatchProfileDetailsRequestSerializer(
            self.profile,
            data={
                "email": "updated@example.com",
                "first_name": "Erika",
                "tel": "987654321",
            },
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        self.user.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(self.user.email, "updated@example.com")
        self.assertEqual(self.profile.first_name, "Erika")
        self.assertEqual(self.profile.tel, "987654321")
        self.assertEqual(self.profile.last_name, "Mustermann")
        self.assertEqual(self.profile.location, "Berlin")

    def test_invalid_email_is_rejected(self):
        """Reject an invalid email before saving any requested changes."""
        serializer = PatchProfileDetailsRequestSerializer(
            self.profile,
            data={
                "email": "invalid-email",
                "location": "Hamburg",
            },
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

        self.user.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(
            self.user.email,
            "customer@example.com",
        )
        self.assertEqual(self.profile.location, "Berlin")

    def test_update_preserves_unrelated_user_fields(self):
        """Keep the username, user type, and password unchanged."""
        original_password = self.user.password

        serializer = PatchProfileDetailsRequestSerializer(
            self.profile,
            data={"email": "new@example.com"},
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        self.user.refresh_from_db()

        self.assertEqual(self.user.username, "testcustomer")
        self.assertEqual(self.user.type, "customer")
        self.assertEqual(self.user.password, original_password)