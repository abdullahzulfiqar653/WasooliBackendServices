from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from apis.models.merchant_member import MerchantMember
from apis.models.merchant import Merchant
from apis.models.invoice import Invoice
from apis.models.member_role import MemberRole


class MemberRetrieveTestCase(APITestCase):
    def setUp(self):
        """Set up test database with a merchant, different owner, and members"""
        self.client = APIClient()

        self.user1 = User.objects.create_user(
            email="testmember122@gmail.com",
            password="testpassword",
            username="testuser11",
        )
        self.user2 = User.objects.create_user(
            email="testmember222@gmail.com",
            password="testpassword",
            username="testuser121",
        )
        self.user3 = User.objects.create_user(
            email="testmember333@gmail.com",
            password="testpassword",
            username="testuser132",
        )

        #  Create a separate user as the merchant owner
        self.owner1 = User.objects.create_user(
            email="owner22@gmail.com",
            password="ownerpassword",
            username="merchantowner123",
        )
        self.owner2 = User.objects.create_user(
            email="owner33@gmail.com",
            password="ownerpassword",
            username="merchantowner1144",
        )

        self.merchant1 = Merchant.objects.create(
            name="Test's Member Business",
            type="Water",
            area="Test Area",
            city="Test City",
            is_advance_payment=True,
            commission_structure={
                "cash": [{"max_credit": 1000, "commission": 0.1}],
                "online": [{"max_credit": 1000, "commission": 0.5}],
            },
            owner=self.owner1,
        )
        self.merchant2 = Merchant.objects.create(
            name="Test's Member Business",
            type="Water",
            area="Test Area",
            city="Test City",
            is_advance_payment=True,
            commission_structure={
                "cash": [{"max_credit": 1000, "commission": 0.1}],
                "online": [{"max_credit": 1000, "commission": 0.5}],
            },
            owner=self.owner2,
        )

        # ✅ Create MerchantMember instances
        self.merchant_member1 = MerchantMember.objects.create(
            user=self.user2,
            merchant=self.merchant1,
            primary_phone="3124567897",
        )
        MemberRole.objects.create(member=self.merchant_member1, role="Customer")
        self.code1 = self.merchant_member1.code
        self.merchant_member1.save()
        self.merchant_member2 = MerchantMember.objects.create(
            user=self.user1,
            merchant=self.merchant2,
            primary_phone="3456765432",
        )
        self.merchant_member3 = MerchantMember.objects.create(
            user=self.user3,
            merchant=self.merchant1,
            primary_phone="3456700432",
        )
        MemberRole.objects.create(member=self.merchant_member3, role="Customer")
        self.code2 = self.merchant_member2.code

        MemberRole.objects.create(member=self.merchant_member2, role="Staff")

        # ✅ Create Invoice instance
        self.invoice1 = Invoice.objects.create(
            member=self.merchant_member1,
            total_amount=500,
            due_amount=100,
            status=Invoice.STATUS.UNPAID,
            type=Invoice.Type.MISCILLANEOUS,
        )

        self.invoice2 = Invoice.objects.create(
            member=self.merchant_member1,
            total_amount=1500,
            due_amount=100,
            status=Invoice.STATUS.PAID,
            type=Invoice.Type.MONTHLY,
        )
        self.invoice4 = Invoice.objects.create(
            member=self.merchant_member1,
            total_amount=78888,
            due_amount=900,
            status=Invoice.STATUS.PAID,
            type=Invoice.Type.MONTHLY,
        )
        self.invoice5 = Invoice.objects.create(
            member=self.merchant_member1,
            total_amount=23456,
            due_amount=900,
            status=Invoice.STATUS.PAID,
            type=Invoice.Type.MISCILLANEOUS,
        )
        self.invoice3 = Invoice.objects.create(
            member=self.merchant_member2,
            total_amount=1900,
            due_amount=100,
            status=Invoice.STATUS.PAID,
            type=Invoice.Type.MISCILLANEOUS,
        )

    def test_valid_customer_invoice(self):
        """Test that a valid customer is correctly created and retrieved"""
        url = f"/api/public/customer/{self.code1}/invoices/"

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertIsInstance(response.data, list)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 4)

    def test_valid_staff_invoice(self):
        """Test that a valid customer is correctly created and retrieved"""
        url = f"/api/public/customer/{self.code2}/invoices/"

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.data)
        self.assertIsInstance(response.data["detail"], list)
        self.assertEqual(response.data["detail"][0], "Member is not a Customer.")

    def test_invalid_customer_code(self):
        """Test that a valid customer is correctly created and retrieved"""
        url = f"/api/public/customer/7890/invoices/"

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.data)
        self.assertIsInstance(response.data["detail"], list)
        self.assertEqual(response.data["detail"][0], "Customer not found.")

    def test_filter_invoices_by_miscellaneous_type(self):
        """Test that invoices are correctly filtered by type (miscellaneous)."""
        url = f"/api/public/customer/{self.code1}/invoices/?type=miscellaneous"

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)

        for invoice in response.data:
            self.assertEqual(invoice["type"], "miscellaneous")

    def test_filter_invoices_by_monthly_type(self):
        """Test that invoices are correctly filtered by type (miscellaneous)."""
        url = f"/api/public/customer/{self.code1}/invoices/?type=monthly"

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)

        for invoice in response.data:
            self.assertEqual(invoice["type"], "monthly")

    def test_filter_invoices_by_invalid_type(self):
        """Test that filtering invoices with an invalid type returns an empty list."""
        url = f"/api/public/customer/{self.code1}/invoices/?type=jshkjshfkj"

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 0)

    def test_filter_invoices_by_status_paid(self):
        """Test that invoices are correctly filtered by status (paid)."""
        url = f"/api/public/customer/{self.code1}/invoices/?status=paid"

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertTrue(
            all(invoice["status"] == "paid" for invoice in response.data),
            "All returned invoices should have status 'paid'.",
        )

    # 2. Filter Invoices by Both status=paid and type=miscellaneous

    def test_filter_invoices_by_status_and_type(self):
        """Test that invoices are correctly filtered by status and type."""
        url = f"/api/public/customer/{self.code1}/invoices/?status=paid&type=miscellaneous"

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertTrue(
            all(
                invoice["status"] == "paid" and invoice["type"] == "miscellaneous"
                for invoice in response.data
            ),
            "All returned invoices should have status 'paid' and type 'miscellaneous'.",
        )

    def test_filter_invoices_by_status_type_and_created_at_year(self):
        """Test invoices filtered by status, type, and created year together."""
        url = f"/api/public/customer/{self.code1}/invoices/?status=paid&type=miscellaneous&created_at_year=2025"

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertTrue(
            all(
                invoice["status"] == "paid"
                and invoice["type"] == "miscellaneous"
                and invoice["created_at"].startswith("2025")
                for invoice in response.data
            ),
            "All returned invoices should have status 'paid', type 'miscellaneous', and be from the year 2025.",
        )
