from apis.models.merchant import Merchant
from apis.models.merchant_member import MerchantMember
from apis.models.merchant_membership import MerchantMembership
from apis.models.supply_record import SupplyRecord


from django.utils import timezone
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import AccessToken


class MemberSupplyRecordListCreateAPIViewTest(APITestCase):
    def setUp(self):
        """Set up test database with a merchant, linked user, membership, and a supply record"""
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

        self.url = f"/api/members/{self.member.id}/supply-record/"

    def test_get_supply_records(self):
        # Create a supply record for today
        today = timezone.now()
        SupplyRecord.objects.create(
            merchant_membership=self.membership,
            given=10,
            taken=5,
            created_at=today,
        )

        # Call the API to get the supply records
        response = self.client.get(
            self.url,
            data={"created_at_year": today.year, "created_at_month": today.month},
        )

        # Ensure that the response is 200 OK and contains the expected data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["given"], 10)
        self.assertEqual(response.data[0]["taken"], 5)

    def test_post_create_supply_record(self):
        # Prepare the data to create a new supply record
        today = timezone.now().date()
        data = {
            "given": 15,
            "taken": 7,
        }

        # Create supply record via POST
        response = self.client.post(self.url, data=data)

        # Ensure that the response is 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Ensure the data is correct in the database
        supply_record = SupplyRecord.objects.get(
            merchant_membership=self.membership, created_at__date=today
        )
        self.assertEqual(supply_record.given, 15)
        self.assertEqual(supply_record.taken, 7)

    def test_post_update_supply_record(self):
        # Create an initial supply record for today
        today = timezone.now()
        SupplyRecord.objects.create(
            merchant_membership=self.membership,
            given=10,
            taken=5,
            created_at=today,
        )

        # Prepare the updated data for the supply record
        updated_data = {
            "given": 12,
            "taken": 6,
        }

        # Update the existing supply record via POST
        response = self.client.post(self.url, data=updated_data)

        # Ensure that the response is 201 Created (since it's updating)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Ensure the record is updated correctly
        supply_record = SupplyRecord.objects.get(
            merchant_membership=self.membership, created_at__date=today
        )
        self.assertEqual(supply_record.given, 12)
        self.assertEqual(supply_record.taken, 6)

    def test_post_create_supply_record_only_one_per_day(self):
        # Create an initial supply record for today
        today = timezone.now()
        SupplyRecord.objects.create(
            merchant_membership=self.membership,
            given=10,
            taken=5,
            created_at=today,
        )

        # Try to create another supply record for the same day
        new_data = {
            "given": 20,
            "taken": 10,
        }

        # This should update the existing record, not create a new one
        response = self.client.post(self.url, data=new_data)

        # Ensure the response is 201 Created (new data should overwrite)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Ensure that the existing supply record is updated
        supply_record = SupplyRecord.objects.get(
            merchant_membership=self.membership, created_at__date=today
        )
        self.assertEqual(supply_record.given, 20)
        self.assertEqual(supply_record.taken, 10)

    def test_get_supply_records_no_records(self):
        # Try fetching supply records when no records exist
        today = timezone.now()
        response = self.client.get(
            self.url,
            data={"created_at_year": today.year, "created_at_month": today.month},
        )

        # Ensure the response is 200 OK and no data is returned
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
