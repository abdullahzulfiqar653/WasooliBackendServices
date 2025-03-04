from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from apis.models.merchant_member import MerchantMember
from apis.models.merchant_membership import MerchantMembership
from apis.models.merchant import Merchant
from apis.models.member_role import MemberRole


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
            actual_price=1000,
            discounted_price=900,  # Example field
        )
        # -----------------------Creating membership of member1 with Merchnat2-------------------------------
        self.merchant_membership2 = MerchantMembership.objects.create(
            merchant=self.merchant2,
            member=self.merchant_member1,  # or self.user2, depending on logic
            is_active=True,
            actual_price=1500,
            discounted_price=1400,
        )

    def test_retrieve_valid_customer(self):

        url = f"/api/public/customer/{self.code1}/merchants/"

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        expected_merchants = [
            {"name": "Test's Member Business"},
            {"name": "Test's Member Business"},
        ]
        actual_merchants = [{"name": merchant["name"]} for merchant in response.data]
        self.assertEqual(actual_merchants, expected_merchants)

        expected_ids = {
            str(self.merchant1.id),
            str(self.merchant2.id),
        }  # Ensure IDs match
        actual_ids = {merchant["id"] for merchant in response.data}

        self.assertEqual(actual_ids, expected_ids)  # Ensure IDs match

    def test_retrieve_member_who_is_notCustomer(self):

        url = f"/api/public/customer/{self.code2}/merchants/"

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

        # Assert error message matches expected message
        self.assertEqual(response.data, {"detail": ["Member is not a Customer."]})

    def test_retrieve_member_dont_exist(self):

        url = f"/api/public/customer/1000000/merchants/"

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

        # Assert error message matches expected message
        self.assertEqual(response.data, {"detail": ["Customer not found."]})
