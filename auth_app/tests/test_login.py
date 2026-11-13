from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import User


class LoginTests(APITestCase):
    """Test login responses, credential validation, and token handling."""

    def setUp(self):
        """Create an active customer and define valid login credentials."""
        self.url = "/api/login/"
        self.password = "Testpasswort123!"

        self.user = User.objects.create_user(
            username="testcustomer",
            email="customer@example.com",
            password=self.password,
            type="customer",
        )

        self.data = {
            "username": self.user.username,
            "password": self.password,
        }

    def test_login_with_valid_credentials(self):
        """Return a matching token and user details for valid credentials."""
        response = self.client.post(
            self.url,
            self.data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        token = Token.objects.get(user=self.user)

        self.assertEqual(response.data["token"], token.key)
        self.assertEqual(response.data["user_id"], self.user.id)
        self.assertEqual(response.data["username"], self.user.username)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertNotIn("password", response.data)

    def test_login_reuses_existing_token(self):
        """Return the existing token instead of creating another one."""
        token, _ = Token.objects.get_or_create(user=self.user)
        token_count_before = Token.objects.count()

        response = self.client.post(
            self.url,
            self.data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["token"], token.key)
        self.assertEqual(Token.objects.count(), token_count_before)

    def test_login_creates_token_if_missing(self):
        """Create a token when a valid user does not already have one."""
        Token.objects.filter(user=self.user).delete()

        response = self.client.post(
            self.url,
            self.data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        token = Token.objects.get(user=self.user)

        self.assertEqual(response.data["token"], token.key)

    def test_login_with_wrong_password(self):
        """Reject an incorrect password without creating a token."""
        Token.objects.filter(user=self.user).delete()
        data = {
            **self.data,
            "password": "FalschesPasswort123!",
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertIn("detail", response.data)
        self.assertNotIn("token", response.data)
        self.assertFalse(
            Token.objects.filter(user=self.user).exists()
        )

    def test_login_with_unknown_username(self):
        """Reject credentials for a user who does not exist."""
        data = {
            **self.data,
            "username": "unknowncustomer",
        }
        token_count_before = Token.objects.count()

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertIn("detail", response.data)
        self.assertNotIn("token", response.data)
        self.assertEqual(Token.objects.count(), token_count_before)

    def test_login_with_missing_required_fields(self):
        """Reject requests missing either username or password."""
        for field in ["username", "password"]:
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
                self.assertNotIn("token", response.data)

    def test_login_with_blank_fields(self):
        """Reject an empty username or password."""
        for field in ["username", "password"]:
            with self.subTest(field=field):
                data = {
                    **self.data,
                    field: "",
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
                self.assertIn(field, response.data)

    def test_login_with_null_fields(self):
        """Reject null values for username or password."""
        for field in ["username", "password"]:
            with self.subTest(field=field):
                data = {
                    **self.data,
                    field: None,
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
                self.assertIn(field, response.data)

    def test_login_with_inactive_user(self):
        """Reject an inactive user even when the credentials are correct."""
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        Token.objects.filter(user=self.user).delete()

        response = self.client.post(
            self.url,
            self.data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertNotIn("token", response.data)
        self.assertFalse(
            Token.objects.filter(user=self.user).exists()
        )

    def test_login_with_business_user(self):
        """Allow a business user to log in with valid credentials."""
        business_user = User.objects.create_user(
            username="testbusiness",
            email="business@example.com",
            password=self.password,
            type="business",
        )

        response = self.client.post(
            self.url,
            {
                "username": business_user.username,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        token = Token.objects.get(user=business_user)

        self.assertEqual(response.data["token"], token.key)
        self.assertEqual(response.data["user_id"], business_user.id)

    def test_get_is_not_allowed(self):
        """Reject GET requests because login requires POST."""
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
