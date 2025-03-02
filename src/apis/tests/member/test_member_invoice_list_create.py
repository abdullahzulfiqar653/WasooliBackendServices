from apis.models.invoice import Invoice
from apis.models.merchant import Merchant
from apis.models.merchant_member import MerchantMember
from apis.models.merchant_membership import MerchantMembership

from decimal import Decimal

from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase, APIClient



class MemberInvoiceListCreateAPITestCase(APITestCase):
    def setUp(self):
        """Set up test database with a merchant, linked user, and membership"""
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

        # Force authentication as merchant user
        self.client.force_authenticate(user=self.user)

        # Define the API URL for the invoices
        self.url = f"/api/members/{self.member.id}/invoices/"

    def test_get_invoices(self):
        # Create some invoices for the member
        invoice_1 = Invoice.objects.create(
            member=self.member,
            total_amount=Decimal(100),
            due_amount=Decimal(100),
            status=Invoice.STATUS.UNPAID,
            type=Invoice.Type.MISCILLANEOUS,
            is_monthly=False,
        )
        invoice_2 = Invoice.objects.create(
            member=self.member,
            total_amount=Decimal(200),
            due_amount=Decimal(200),
            status=Invoice.STATUS.PAID,
            type=Invoice.Type.MISCILLANEOUS,
            is_monthly=False,
        )

        # GET request to fetch invoices
        response = self.client.get(self.url)

        # Assert the response status and content
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Two invoices created

        # Test with filters
        response = self.client.get(self.url, {"created_at_year": "2024"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_invoice(self):
        # Data to create a new invoice
        data = {
            "total_amount": "500.00",
            "metadata": {"remarks": "New invoice creation"},
            "mark_paid": False,
        }

        # POST request to create a new invoice
        response = self.client.post(self.url, data, format="json")

        # Assert the response status and created invoice details
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["total_amount"], "500.00")
        self.assertEqual(response.data["status"], "unpaid")
        self.assertEqual(response.data["metadata"]["remarks"], "New invoice creation")
