from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from apis.models.merchant import Merchant
from apis.models.merchant_member import MerchantMember
from apis.models.transaction_history import TransactionHistory
from apis.models.merchant_membership import MerchantMembership


User = get_user_model()


class TestMerchantDashboardRetrieve(APITestCase):

    def setUp(self):
        """Set up test database with a merchant, linked user, and membership"""
        self.client = APIClient()

        # Create a test user
        self.user = User.objects.create_user(
            email="testuserdashbboard@gmail.com",
            password="testpassword",
            username="testuserdashboard",
        )

        # Create a merchant
        self.merchant = Merchant.objects.create(
            name="Test's Water Business",
            type="Water",
            area="Test area",
            city="Rahim Yar Khan",
            is_advance_payment=True,
            commission_structure={
                "cash": [{"max_credit": 1000, "commission": 0.1}],
                "online": [{"max_credit": 1000, "commission": 0.5}],
            },
            owner=self.user,
        )

        # Create MerchantMembership and link to Merchant
        self.merchant_membership = MerchantMember.objects.create(
            user=self.user,
            merchant=self.merchant,
            primary_phone="3186531138",
            code="1001",
        )

        #  Now assign the membership properly
        self.merchant.membership = self.merchant_membership
        self.merchant.save()

        # Force authentication
        self.client.force_authenticate(user=self.user)

    def test_dashboard_access(self):
        """Test that the dashboard API returns data for the merchant"""
        url = f"/api/merchants/{self.merchant.id}/dashboard/"

        response = self.client.get(url)
        response_data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertIn("total_collections_today", response_data)

    def test_dashboard_access_unauthorized_user(self):
        """Test that a user cannot access another merchant's dashboard"""
        other_user = User.objects.create_user(
            email="unauthorized@gmail.com",
            password="testpassword",
            username="unauthorized_user",
        )

        # Create another merchant owned by this new user
        other_merchant = Merchant.objects.create(
            name="Another Merchant",
            type="Retail",
            area="Somewhere",
            city="Some City",
            is_advance_payment=False,
            commission_structure={
                "cash": [{"max_credit": 2000, "commission": 0.2}],
                "online": [{"max_credit": 2000, "commission": 0.6}],
            },
            owner=other_user,
        )

        # ✅ Create a profile for the unauthorized user as well
        other_user.profile = MerchantMember.objects.create(
            user=other_user,
            merchant=other_merchant,
            primary_phone="3000000000",
            code="1002",
        )

        # Logout the previous user
        self.client.logout()

        # Authenticate as the second user (unauthorized user)
        self.client.force_authenticate(user=other_user)

        # Attempt to access the first merchant's dashboard
        url = f"/api/merchants/{self.merchant.id}/dashboard/"
        response = self.client.get(url)

        # Assertions
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN
        )  # Should return 403 Forbidden
        self.assertEqual(
            response.json(),
            {"detail": "You do not have permission to perform this action."},
        )

    def test_dashboard_invalid_merchant(self):
        """Test that accessing a non-existent merchant's dashboard returns 404"""

        invalid_merchant_id = 999999  # An ID that doesn't exist
        url = f"/api/merchants/{invalid_merchant_id}/dashboard/"

        response = self.client.get(url)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json(), {"detail": ["Matching id not found."]})

    def test_dashboard_access_unauthenticated_user(self):
        """Test that an unauthenticated user cannot access the merchant dashboard"""

        #  Ensure no user is authenticated
        self.client.logout()

        # Attempt to access the merchant's dashboard
        url = f"/api/merchants/{self.merchant.id}/dashboard/"
        response = self.client.get(url)

        #  Assertions
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED
        )  # Must return 401 Unauthorized
        self.assertEqual(
            response.json(), {"detail": "Authentication credentials were not provided."}
        )  # Ensure expected error message

    def test_dashboard_invalid_auth_token(self):
        """Test accessing dashboard with an invalid authentication token"""
        # Simulate an invalid authentication token
        self.client.logout()

        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid_token_123")

        url = f"/api/merchants/{self.merchant.id}/dashboard/"
        response = self.client.get(url)

        # ✅ Expected: 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.json(),
            {
                "detail": "Given token not valid for any token type",
                "code": "token_not_valid",
                "messages": [
                    {
                        "token_class": "AccessToken",
                        "token_type": "access",
                        "message": "Token is invalid or expired",
                    }
                ],
            },
        )

    def test_dashboard_with_transactions(self):
        """Test that the dashboard API correctly calculates total collections when transactions exist"""

        # Ensure no duplicate user error
        User.objects.filter(username="testuser").delete()
        User.objects.filter(username="testuser_owner").delete()

        #  Create test users
        test_owner = User.objects.create(username="testuser_owner")
        user = User.objects.create(username="testuser")

        # Authenticate as test_owner
        self.client.force_authenticate(user=test_owner)

        # Create a merchant owned by test_owner
        merchant = Merchant.objects.create(name="Test Merchant", owner=test_owner)

        member = MerchantMember.objects.create(merchant=merchant, user=user)

        membership = MerchantMembership.objects.create(
            member=member,
            merchant=merchant,
            actual_price=180.00,
            discounted_price=90.00,
        )

        merchant.membership = membership
        merchant.save()

        TransactionHistory.objects.create(
            merchant_membership=membership,
            credit=500,
            transaction_type=TransactionHistory.TRANSACTION_TYPE.CREDIT,
            type=TransactionHistory.TYPES.BILLING,
            created_at=timezone.now(),
        )

        TransactionHistory.objects.create(
            merchant_membership=membership,
            credit=700,
            transaction_type=TransactionHistory.TRANSACTION_TYPE.CREDIT,
            type=TransactionHistory.TYPES.BILLING,
            created_at=timezone.now(),
        )

        # ✅ Call the dashboard API

        url = f"/api/merchants/{merchant.id}/dashboard/"
        response = self.client.get(url)
        response_data = response.json()

        # ✅ Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("total_collections_today", response_data)

        # Verify that the sum of today’s transactions is correctly calculated (500 + 300)
        self.assertEqual(response_data["total_collections_this_month"]["value"], 1200)
