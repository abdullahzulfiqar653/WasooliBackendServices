from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()


class TestRefreshTokenAPIView(TestCase):
    def setUp(self):
        """Set up test data for Refresh Token API"""
        self.client = APIClient()

        # Create test user
        self.user = User.objects.create_user(
            email="testuser@gmail.com", password="testpassword", username="test_user"
        )

        # Generate valid refresh token
        refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(refresh)
        print("Generated Refresh Token:", self.refresh_token)

        self.client.cookies.load(
            {"wasooli_refresh_token": self.refresh_token}
        )  # Manually set cookies
        print("Cookies after load:", self.client.cookies)

        # API endpoint
        self.url = "/api/auth/refresh-token/"

    def test_refresh_token_success(self):
        """Test that a new access token is returned for a valid refresh token"""

        # Set valid refresh token in cookies
        self.client.cookies["wasooli_refresh_token"] = self.refresh_token
        print(self.client.cookies)

        response = self.client.get(self.url)  # Retrieve access token

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)  # Ensure access token is returned

    def test_refresh_token_missing(self):
        """Test that missing refresh token returns authentication error"""

        self.client.cookies.clear()  # Ensure no cookies are set
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "No refresh token found in cookies")

    def test_refresh_token_invalid(self):
        """Test that an invalid refresh token returns authentication error"""

        # Set invalid refresh token in cookies
        self.client.cookies["wasooli_refresh_token"] = "invalid_refresh_token"

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Invalid Refresh Token.")
