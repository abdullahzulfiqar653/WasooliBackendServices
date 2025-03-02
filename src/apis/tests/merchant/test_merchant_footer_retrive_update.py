from apis.models.merchant import Merchant

from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase

import json


class MerchantFooterRetrieveUpdateAPIViewTest(APITestCase):
    def setUp(self):
        """Set up test data including merchant and user."""
        self.user = User.objects.create_user(
            username="merchant_user", password="testpass"
        )
        self.merchant = Merchant.objects.create(
            name="Test Merchant",
            type=Merchant.MerchantType.GYM,
            owner=self.user,
            area="Test Area",
            city="Test City",
            metadata={
                "footer": {
                    "phone": "1234567890",
                    "address": "Old Address",
                    "note": "Closed on Sundays",
                }
            },
        )
        self.client.force_authenticate(user=self.user)
        self.url = f"/api/merchants/{self.merchant.id}/footer/"

    def test_retrieve_footer_metadata(self):
        """Test retrieving footer metadata."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("metadata", response.data)
        self.assertEqual(response.data["metadata"], self.merchant.metadata)

    def test_update_footer_metadata(self):
        """Test updating footer metadata."""
        new_metadata = {
            "metadata": {
                "phone": "3103987654",
                "address": "Gulshan Usman",
                "note": "We are open 24/7",
                "email": "testing123@gmail.com",
            }
        }
        response = self.client.put(
            self.url, data=json.dumps(new_metadata), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.merchant.refresh_from_db()
        self.assertEqual(self.merchant.metadata["footer"], new_metadata["metadata"])
