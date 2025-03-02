from django.utils import timezone
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient, APITestCase

from apis.models.supply_record import SupplyRecord
from apis.models import Merchant, MerchantMember, MerchantMembership


class MemberProfileRetrieveTestCase(APITestCase):

    def setUp(self):
        """Set up test database with a merchant, linked user, and membership"""
        # Initialize API client for making requests
        self.client = APIClient()

        # Create a test merchant user
        self.user = get_user_model().objects.create_user(
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

        # Authenticate the user for making requests
        self.client.force_authenticate(user=self.user)

        # Define the API URL for the member profile retrieval endpoint
        self.url = f"/api/members/{self.member.id}/profile/"

        # Optionally create supply records if needed for  test
        today = timezone.now()
        SupplyRecord.objects.create(
            merchant_membership=self.membership,
            given=10,
            taken=5,
            created_at=today,
        )

    def test_member_profile_retrieve(self):
        """Test retrieval of member profile"""
        response = self.client.get(self.url)

        # Check the response status
        self.assertEqual(response.status_code, 200)

        # Check the structure of the response data
        response_data = response.json()

        # Ensure that required fields are present in the response
        self.assertIn("total_spend", response_data)
        self.assertIn("user_amounts_balance", response_data)
        self.assertIn("total_saved", response_data)

        # Further checks on the 'total_spend' field
        self.assertIsInstance(response_data["total_spend"], dict)
        self.assertIn("value", response_data["total_spend"])
        self.assertIsInstance(response_data["total_spend"]["value"], (float, int))
        self.assertIn("name", response_data["total_spend"])
        self.assertEqual(response_data["total_spend"]["name"], "Total Spend")

        # Further checks on the 'user_amounts_balance' field
        self.assertIsInstance(response_data["user_amounts_balance"], dict)
        self.assertIn("value", response_data["user_amounts_balance"])
        self.assertIsInstance(
            response_data["user_amounts_balance"]["value"], (float, int)
        )
        self.assertIn("name", response_data["user_amounts_balance"])
        self.assertEqual(response_data["user_amounts_balance"]["name"], "Balance")

        # Further checks on the 'total_saved' field
        self.assertIsInstance(response_data["total_saved"], dict)
        self.assertIn("value", response_data["total_saved"])
        self.assertIsInstance(response_data["total_saved"]["value"], (float, int))
        self.assertIn("name", response_data["total_saved"])
        self.assertEqual(response_data["total_saved"]["name"], "Total Saved")
