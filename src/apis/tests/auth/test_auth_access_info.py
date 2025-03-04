from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apis.models.merchant import Merchant
from apis.models.merchant_member import MerchantMember
from apis.models.member_role import MemberRole, RoleChoices

User = get_user_model()


class TestAccessInfoRetrieveAPIView(TestCase):
    def setUp(self):
        """Set up test data for Access Info API"""
        self.client = APIClient()

        # Create test user
        self.user = User.objects.create_user(
            email="testuser@gmail.com", password="testpassword", username="testuser"
        )

        # Create a merchant
        self.merchant = Merchant.objects.create(
            name="Test Merchant",
            type="Retail",
            area="Test Area",
            city="Test City",
            is_advance_payment=True,
            owner=self.user,
        )

        # Create a merchant member linked to the merchant
        self.merchant_member = MerchantMember.objects.create(
            user=self.user,
            merchant=self.merchant,
            primary_phone="3123456789",
            code="1234",
        )

        # Assign a role to user
        self.role = MemberRole.objects.create(
            member=self.merchant_member, role=RoleChoices.MERCHANT
        )

        # Authenticate user
        self.client.force_authenticate(user=self.user)

    def test_access_info_retrieve_success(self):
        """Test retrieving access info for an authenticated merchant user"""
        url = "/api/auth/access-info/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["is_merchant"], True)
        self.assertEqual(response.data["merchant_id"], self.merchant.id)
        self.assertEqual(response.data["member_id"], self.merchant_member.id)
        self.assertIn("permissions", response.data)

    def test_access_info_unauthorized(self):
        """Test access info retrieval fails for unauthenticated user"""
        self.client.logout()  # Logout user
        url = "/api/auth/access-info/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
