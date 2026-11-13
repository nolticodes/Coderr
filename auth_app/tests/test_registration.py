from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from profile_app.models import Profile
from auth_app.models import User


class RegistrationTests(APITestCase):
    """Test successful registration and rejection of invalid registration data."""

    def test_registration_with_valid_data(self):
        """Verify user, profile, token, password hashing, and response data."""
        data = {
            "username": "testcustomer",
            "email": "test@example.com",
            "password": "Testpasswort123!",
            "repeated_password": "Testpasswort123!",
            "type": "customer",
        }

        response = self.client.post(
            "/api/registration/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertTrue(
            User.objects.filter(username="testcustomer").exists()
        )

        user = User.objects.get(username=data["username"])

        self.assertTrue(user.check_password(data["password"]))
        self.assertNotEqual(user.password, data["password"])

        self.assertTrue(
            Profile.objects.filter(user=user).exists()
        )

        token = Token.objects.get(user=user)
        self.assertEqual(response.data["token"], token.key)

        self.assertEqual(response.data["user_id"], user.id)
        self.assertEqual(response.data["username"], user.username)
        self.assertEqual(response.data["email"], user.email)

        self.assertNotIn("password", response.data)
        self.assertNotIn("repeated_password", response.data)

    def test_registration_with_mismatched_passwords(self):
        """Reject mismatched passwords without creating a user."""
        data = {
            "username": "testcustomer",
            "email": "test@example.com",
            "password": "Testpasswort123!",
            "repeated_password": "AnderesPasswort123!",
            "type": "customer",
        }
        user_count_before = User.objects.count()

        response = self.client.post(
            "/api/registration/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("non_field_errors", response.data)
        self.assertEqual(User.objects.count(), user_count_before)

    def test_registration_with_existing_email(self):
        """Reject an existing email address without creating another user."""
        User.objects.create_user(
            username="existingcustomer",
            email="test@example.com",
            password="ExistingPasswort123!",
            type="customer",
        )

        data = {
            "username": "newcustomer",
            "email": "test@example.com",
            "password": "Testpasswort123!",
            "repeated_password": "Testpasswort123!",
            "type": "customer",
        }
        user_count_before = User.objects.count()

        response = self.client.post(
            "/api/registration/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("email", response.data)
        self.assertEqual(User.objects.count(), user_count_before)

    def test_registration_with_existing_username(self):
        """Reject an existing username without creating another user."""
        User.objects.create_user(
            username="testcustomer",
            email="existing@example.com",
            password="ExistingPasswort123!",
            type="customer",
        )

        data = {
            "username": "testcustomer",
            "email": "new@example.com",
            "password": "Testpasswort123!",
            "repeated_password": "Testpasswort123!",
            "type": "customer",
        }
        user_count_before = User.objects.count()

        response = self.client.post(
            "/api/registration/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("username", response.data)
        self.assertEqual(User.objects.count(), user_count_before)

    def test_registration_with_invalid_email(self):
        """Reject an invalid email format without creating a user."""
        data = {
            "username": "testcustomer",
            "email": "keine-gueltige-email",
            "password": "Testpasswort123!",
            "repeated_password": "Testpasswort123!",
            "type": "customer",
        }
        user_count_before = User.objects.count()

        response = self.client.post(
            "/api/registration/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("email", response.data)
        self.assertEqual(User.objects.count(), user_count_before)

    def test_registration_with_missing_required_fields(self):
        """Reject each missing required field without creating a user."""
        required_fields = [
            "username",
            "email",
            "password",
            "repeated_password",
        ]

        for field in required_fields:
            with self.subTest(field=field):
                data = {
                    "username": "testcustomer",
                    "email": "test@example.com",
                    "password": "Testpasswort123!",
                    "repeated_password": "Testpasswort123!",
                    "type": "customer",
                }
                data.pop(field)
                user_count_before = User.objects.count()

                response = self.client.post(
                    "/api/registration/",
                    data,
                    format="json",
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_400_BAD_REQUEST,
                )
                self.assertIn(field, response.data)
                self.assertEqual(
                    User.objects.count(),
                    user_count_before,
                )

    def test_registration_with_invalid_type(self):
        """Reject an unsupported user type without creating a user."""
        data = {
            "username": "testcustomer",
            "email": "test@example.com",
            "password": "Testpasswort123!",
            "repeated_password": "Testpasswort123!",
            "type": "admin",
        }
        user_count_before = User.objects.count()

        response = self.client.post(
            "/api/registration/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("type", response.data)
        self.assertEqual(User.objects.count(), user_count_before)

    def test_registration_with_business_type(self):
        """Verify business registration creates a user, profile, and matching token."""
        data = {
            "username": "testbusiness",
            "email": "business@example.com",
            "password": "Testpasswort123!",
            "repeated_password": "Testpasswort123!",
            "type": "business",
        }

        response = self.client.post(
            "/api/registration/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        user = User.objects.get(username=data["username"])

        self.assertEqual(user.type, "business")
        self.assertTrue(user.check_password(data["password"]))
        self.assertTrue(Profile.objects.filter(user=user).exists())

        token = Token.objects.get(user=user)
        self.assertEqual(response.data["token"], token.key)
