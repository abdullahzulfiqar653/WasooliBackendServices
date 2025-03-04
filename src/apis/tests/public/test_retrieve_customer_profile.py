from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from apis.models.merchant_member import MerchantMember
from apis.models.merchant_membership import MerchantMembership
from apis.models.merchant import Merchant
from apis.models.member_role import MemberRole
from apis.models.invoice import Invoice
from apis.models.transaction_history import TransactionHistory


class MemberRetrieveTestCase(APITestCase):
    def setUp(self):
        """Set up test database with a merchant, different owner, and membership"""
        self.client = APIClient()

        self.owner1 = User.objects.create_user(
            email="testuser100@gmail.com",
            password="testpassword",
            username="testuser100",
        )
        self.owner2 = User.objects.create_user(
            email="testuser101@gmail.com",
            password="testpassword",
            username="testuser101",
        )
        self.owner3 = User.objects.create_user(
            email="testuser102@gmail.com",
            password="testpassword",
            username="testuser102",
        )

        # ✅ Create a separate user as the merchant owner
        self.user = User.objects.create_user(
            email="memberuser@gmail.com",
            password="memberuser123",
            username="memberuser",
        )
        # -------------------------Creating first Merchant------------------------------------------
        self.merchant1 = Merchant.objects.create(
            name="Test's Member Business",
            type="Water",
            area="Test Area1",
            city="Test City1",
            is_advance_payment=True,
            commission_structure={
                "cash": [{"max_credit": 1000, "commission": 0.1}],
                "online": [{"max_credit": 1000, "commission": 0.5}],
            },
            owner=self.owner1,
        )
        self.id_merchant1 = self.merchant1.id
        # ------------------------Creating second Merchant--------------------------
        self.merchant2 = Merchant.objects.create(
            name="Test's Member Business",
            type="Retail",
            area="Test Area2",
            city="Test City2",
            is_advance_payment=True,
            commission_structure={
                "cash": [{"max_credit": 1000, "commission": 0.1}],
                "online": [{"max_credit": 1000, "commission": 0.5}],
            },
            owner=self.owner2,
        )
        self.id_merchant2 = self.merchant2.id
        # ------------------------------Creating 3rd Merchant---------------------------
        self.merchant3 = Merchant.objects.create(
            name="Test's Member Business3",
            type="Retail",
            area="Test Area3",
            city="Test City3",
            is_advance_payment=True,
            owner=self.owner3,
        )
        self.id_merchant3 = self.merchant3.id

        # ---------------------------------Creating Member1 who is Customer--------------------------

        self.merchant_member1 = MerchantMember.objects.create(
            user=self.user,
            primary_phone="3456765432",
        )
        MemberRole.objects.create(member=self.merchant_member1, role="Customer")
        self.code1 = self.merchant_member1.code

        # ---------------------------------Creating Member1 who is Customer--------------------------
        self.user1 = User.objects.create(
            username="testuser108", password="testpassword"
        )

        self.merchant_member2 = MerchantMember.objects.create(
            user=self.user1,
            primary_phone="3456005432",
        )
        MemberRole.objects.create(member=self.merchant_member2, role="Staff")
        self.code2 = self.merchant_member2.code

        # ----------------------Creating Membership of member1 with the merchant1-------------------
        self.merchant_membership1 = MerchantMembership.objects.create(
            merchant=self.merchant1,
            member=self.merchant_member1,  # or self.user2, depending on logic
            is_active=True,
            actual_price=1000000,
            discounted_price=900000,  # Example field
        )
        # -----------------------Creating membership of member1 with Merchnat2-------------------------------
        self.merchant_membership2 = MerchantMembership.objects.create(
            merchant=self.merchant2,
            member=self.merchant_member1,  # or self.user2, depending on logic
            is_active=True,
            actual_price=1500,
            discounted_price=1400,  # Example field
        )

        # ----------------------_Creating Transaction of membership1---------------------------------------
        transaction = TransactionHistory.objects.create(
            merchant_membership=self.merchant_membership1,
            debit=1001,
            credit=101,
            balance=10000,
            transaction_type=TransactionHistory.TRANSACTION_TYPE.DEBIT,
            type=TransactionHistory.TYPES.BILLING,
            is_online=False,
        )
        transactions = TransactionHistory.objects.filter(
            merchant_membership=self.merchant_membership1
        )

        # ----------------------_Creating Transaction of membership2---------------------------------------
        transaction1 = TransactionHistory.objects.create(
            merchant_membership=self.merchant_membership2,
            debit=10010,
            credit=1010,
            balance=10000,
            transaction_type=TransactionHistory.TRANSACTION_TYPE.DEBIT,
            type=TransactionHistory.TYPES.BILLING,
            is_online=False,
        )

    def test_retrieve_customer_profile(self):
        url = f"/api/public/customer/{self.code1}/profile/{self.id_merchant1}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_invalidcustomer_profile(self):
        url = f"/api/public/customer/109887/profile/{self.id_merchant1}/"
        response = self.client.get(url)

        try:
            response_data = response.json()  # If response is JSON

        except Exception:
            response_data = response.content.decode()  # Otherwise, decode raw content

        # Assert response status
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Assert error message in response
        self.assertEqual(response_data, {"detail": ["Customer not found."]})

    def test_retrieve_customer_profile_with_invalid_merchant_id(self):
        url = f"/api/public/customer/{self.code1}/profile/{self.id_merchant3}/"
        response = self.client.get(url)
        response_data = response.json()

        # Assert response status
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_data, {"detail": ["Customer Membership not found."]})
