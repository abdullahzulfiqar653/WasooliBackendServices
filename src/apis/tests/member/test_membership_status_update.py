from apis.models.merchant import Merchant
from apis.models.merchant_member import MerchantMember
from apis.models.merchant_membership import MerchantMembership

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase


User = get_user_model()


class MembershipStatusUpdateApiTestCase(APITestCase):

    def setUp(self):
        """Set up test database with a merchant, linked user, and membership."""
        self.client = APIClient()

        # Create a test merchant user
        self.user = User.objects.create_user(
            email="merchantuser@gmail.com",
            password="merchantpassword",
            username="merchantuser",
        )

        # Create a merchant and assign the owner
        self.merchant = Merchant.objects.create(
            name="Test's Water Business",
            type="Water",
            area="Test Area",
            city="Rahim Yar Khan",
            is_advance_payment=True,
            owner=self.user,
        )

        # Create a MerchantMember (linking user with the merchant)
        self.member = MerchantMember.objects.create(
            user=self.user,
            merchant=self.merchant,
            primary_phone="3186531138",
            code="1001",
        )

        # Create a MerchantMembership (assign membership to the member)
        self.membership = MerchantMembership.objects.create(
            member=self.member,
            merchant=self.merchant,
            is_active=True,
            actual_price=100,
            discounted_price=90,
        )

        # Force authentication as merchant user
        self.client.force_authenticate(user=self.user)

        # Define the API URL for the membership status update
        self.url = f"/api/members/{self.member.id}/status/"

    def test_activate_membership(self):
        """Test activating a membership."""
        response = self.client.patch(self.url, {"is_active": True}, format="json")
        self.membership.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.membership.is_active)

    def test_deactivate_membership(self):
        """Test deactivating a membership."""
        response = self.client.patch(self.url, {"is_active": False}, format="json")
        self.membership.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.membership.is_active)

    def test_unauthorized_user_cannot_update(self):
        """Test that an unauthorized user cannot update the membership status."""
        self.client.logout()  # Remove authentication
        response = self.client.patch(self.url, {"is_active": False}, format="json")

        self.assertEqual(response.status_code, 401)

    def test_invalid_data(self):
        """Test invalid data handling."""
        response = self.client.patch(
            self.url, {"is_active": "invalid_value"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
