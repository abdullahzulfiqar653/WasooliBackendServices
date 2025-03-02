from apis.models.merchant import Merchant
from apis.models.merchant_member import MerchantMember
from apis.models.merchant_membership import MerchantMembership
from apis.models.transaction_history import TransactionHistory

from decimal import Decimal
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.test import APITestCase, APIClient


class MemberTransactionHistoryListCreateAPIViewTest(APITestCase):

    def setUp(self):
        """Set up test database with a merchant, linked user, and membership."""
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
            commission_structure={
                "cash": [{"max_credit": 1000, "commission": 0.1}],
                "online": [{"max_credit": 1000, "commission": 0.5}],
            },
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

        # Generate and assign JWT token for authentication
        self.token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        # Define the API URL for the transaction history
        self.url = f"/api/members/{self.member.id}/transaction-history/"

    def test_list_transaction_history(self):
        """Test listing the transaction history."""
        # Create a dummy transaction for the member
        transaction = TransactionHistory.objects.create(
            merchant_membership=self.membership,
            debit=0,
            credit=150.00,
            balance=150.00,
            metadata="Test transaction",
            is_online=False,
            transaction_type=TransactionHistory.TRANSACTION_TYPE.CREDIT,
            type=TransactionHistory.TYPES.BILLING,
        )

        # Send GET request to fetch the transaction history
        response = self.client.get(self.url)

        # Assert status code and response data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], transaction.id)
        self.assertEqual(
            Decimal(response.data[0]["credit"]), Decimal(str(transaction.credit))
        )

    def test_create_transaction_history(self):
        """Test creating a new transaction history."""
        # Prepare data for a new transaction
        transaction_data = {"amount": "200.00"}

        # Send POST request to create a new transaction
        response = self.client.post(self.url, transaction_data, format="json")

        # Assert status code and that transaction is created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TransactionHistory.objects.count(), 1)
        transaction = TransactionHistory.objects.first()

        # Assert the transaction has correct values
        self.assertEqual(str(transaction.credit), "200.00")
        self.assertEqual(transaction.merchant_membership, self.membership)
        self.assertEqual(
            transaction.transaction_type, TransactionHistory.TRANSACTION_TYPE.CREDIT
        )

    def test_create_transaction_history_invalid_amount(self):
        """Test creating a new transaction history with invalid amount."""
        # Prepare data with invalid (negative) amount
        transaction_data = {"amount": "-50.00"}

        # Send POST request to create a new transaction
        response = self.client.post(self.url, transaction_data, format="json")

        # Assert status code for invalid input (Bad request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Amount must be greater than 0", str(response.data))
