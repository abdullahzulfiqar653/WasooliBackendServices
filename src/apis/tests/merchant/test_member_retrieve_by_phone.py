from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apis.models.merchant import Merchant
from apis.models.merchant_member import MerchantMember

User = get_user_model()


class TestMerchantRetrieve(TestCase):
    def setUp(self):
        """Set up test database with a merchant, linked user, and membership"""
        self.client = APIClient()

        # Create a test user
        self.user = User.objects.create_user(
            email="test@gmail.com", password="testpassword", username="testuser"
        )

        # Create a merchant
        self.merchant = Merchant.objects.create(
            name="Test's Water Business",
            type="Water",
            area="test Area",
            city="Test City",
            is_advance_payment=True,
            commission_structure={
                "cash": [{"max_credit": 1000, "commission": 0.1}],
                "online": [{"max_credit": 1000, "commission": 0.5}],
            },
            owner=self.user,
        )

        # ✅ Create MerchantMembership and link to Merchant
        self.merchant_membership = MerchantMember.objects.create(
            user=self.user,
            merchant=self.merchant,
            primary_phone="3186531138",
            code="1001",
        )

        # ✅ Now assign the membership properly
        self.merchant.membership = self.merchant_membership
        self.merchant.save()

        # Force authentication
        self.client.force_authenticate(user=self.user)

    def test_member_retrieve_by_phone_valid(self):
        # Create a MerchantMember with a primary phone number

        data = {
            "user": {"email": "test@gmail.com", "first_name": "testuser"},
            "cnic": "3130325676738",  # Correct CNIC
            "roles": {"role": "Customer"},  # Ensure 'member' is a valid choice
            "picture": "string",
            "primary_phone": "2378478342",  # Correct phone number
            "merchant_memberships": {
                "area": "test-area",
                "city": "test_city",
                "picture": "string",
                "address": "string",
                "is_active": True,
                "meta_data": "string",
                "is_monthly": True,
                "actual_price": "276",  # Corrected to a positive value
                "secondary_phone": "2318478342",  # Correct phone number
                "discounted_price": "245.70",  # Corrected to a positive value
            },
        }
        url = f"/api/merchants/{self.merchant.id}/members/"

        response = self.client.post(url, data, format="json")
        print("hdfjksdbfkjdsfk", response.data)

        primary_phone = response.data.get("primary_phone")

        # Define the URL for retrieving the member by phone number
        url = f"/api/merchants/{self.merchant.id}/members/{primary_phone}/"

        # Send GET request to the API
        response = self.client.get(url)

        # Check if the response status is OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if the response contains the correct phone number
        self.assertEqual(response.data["primary_phone"], "2378478342")

    def test_member_retrieve_by_phone_invalid(self):
        # Trying to retrieve a member with a non-existent phone number
        url = f"/api/merchants/{self.merchant.id}/members/9999999999/"
        response = self.client.get(url)

        # Assert that the status code is 'Not Found' for invalid phone number
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
