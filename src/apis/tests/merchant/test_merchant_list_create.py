from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apis.models.merchant import Merchant
from apis.models.merchant_member import MerchantMember

User = get_user_model()


class TestMerchantListCreate(TestCase):
    def setUp(self):
        """Set up test database with a merchant, linked user, and membership"""
        self.client = APIClient()

        # Create a test user
        self.user = User.objects.create_user(
            email="fiza13270@gmail.com", password="testpassword", username="fiza13270"
        )

        # Create a merchant
        self.merchant = Merchant.objects.create(
            name="Tests's Water Business",
            type="Water",
            area="Test Area",
            city="Test City",
            is_advance_payment=True,
            commission_structure={
                "cash": [{"max_credit": 1000, "commission": 0.1}],
                "online": [{"max_credit": 1000, "commission": 0.5}],
            },
            owner=self.user,
        )

        # ✅ Create MerchantMembership and link to Merchant
        self.merchant_membership = MerchantMember.objects.create(
            user=self.user,
            merchant=self.merchant,
            primary_phone="3186531138",
            code="1001",
        )

        # ✅ Now assign the membership properly
        self.merchant.membership = self.merchant_membership
        self.merchant.save()

        # Force authentication
        self.client.force_authenticate(user=self.user)

    # -------Creating Member using this api------------------------#

    def test_create_merchant_member(self):

        url = f"/api/merchants/{self.merchant.id}/members/"

        data = {
            "user": {"email": "test@gmail.com", "first_name": "testuser"},
            "cnic": "3130325676738",  # Correct CNIC
            "roles": {"role": "Customer"},  # Ensure 'member' is a valid choice
            "picture": "string",
            "primary_phone": "2378478342",  # Correct phone number
            "merchant_memberships": {
                "area": "test-area",
                "city": "test_city",
                "picture": "string",
                "address": "string",
                "is_active": True,
                "meta_data": "string",
                "is_monthly": True,
                "actual_price": "276",  # Corrected to a positive value
                "secondary_phone": "2378478342",  # Correct phone number
                "discounted_price": "245.70",  # Corrected to a positive value
            },
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"]["email"], "test@gmail.com")
        self.assertEqual(response.data["user"]["first_name"], "testuser")
        self.assertEqual(response.data["cnic"], "3130325676738")
        self.assertEqual(response.data["primary_phone"], "2378478342")

    def test_create_merchant_member_missing_fields(self):
        url = f"/api/merchants/{self.merchant.id}/members/"

        # Omitting the required 'cnic' field
        data = {
            "user": {"email": "test@gmail.com", "first_name": "testuser"},
            "roles": {"role": "Customer"},
            "primary_phone": "2378478342",
            "merchant_memberships": {
                "area": "test-area",
                "city": "test_city",
                "picture": "string",
                "address": "string",
                "is_active": True,
                "meta_data": "string",
                "is_monthly": True,
                "actual_price": "276",
                "secondary_phone": "2378478342",
                "discounted_price": "245.70",
            },
        }

        response = self.client.post(url, data, format="json")

        # Check for a bad request status due to the missing CNIC field
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_merchant_member_invalid_data(self):
        url = f"/api/merchants/{self.merchant.id}/members/"

        # Invalid CNIC (too short)
        data = {
            "user": {"email": "test@gmail.com", "first_name": "testuser"},
            "cnic": "12345",  # Invalid CNIC
            "roles": {"role": "Customer"},
            "primary_phone": "2378478342",
            "merchant_memberships": {
                "area": "test-area",
                "city": "test_city",
                "picture": "string",
                "address": "string",
                "is_active": True,
                "meta_data": "string",
                "is_monthly": True,
                "actual_price": "276",
                "secondary_phone": "2378478342",
                "discounted_price": "245.70",
            },
        }

        response = self.client.post(url, data, format="json")

        # Expecting a validation error due to invalid CNIC
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_merchant_member_invalid_role(self):
        url = f"/api/merchants/{self.merchant.id}/members/"

        # Invalid role, assuming 'InvalidRole' is not a valid role
        data = {
            "user": {"email": "test@gmail.com", "first_name": "testuser"},
            "cnic": "3130325676738",  # Correct CNIC
            "roles": {"role": "InvalidRole"},  # Invalid role
            "primary_phone": "2378478342",
            "merchant_memberships": {
                "area": "test-area",
                "city": "test_city",
                "picture": "string",
                "address": "string",
                "is_active": True,
                "meta_data": "string",
                "is_monthly": True,
                "actual_price": "276",
                "secondary_phone": "2378478342",
                "discounted_price": "245.70",
            },
        }

        response = self.client.post(url, data, format="json")

        # Expecting a validation error for invalid role
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_merchant_member_invalid_primary_phone(self):
        url = f"/api/merchants/{self.merchant.id}/members/"

        # Invalid phone number format (too short)
        data = {
            "user": {"email": "test@gmail.com", "first_name": "testuser"},
            "cnic": "3130325676738",  # Correct CNIC
            "roles": {"role": "Customer"},
            "primary_phone": "123",  # Invalid phone number
            "merchant_memberships": {
                "area": "test-area",
                "city": "test_city",
                "picture": "string",
                "address": "string",
                "is_active": True,
                "meta_data": "string",
                "is_monthly": True,
                "actual_price": "276",
                "secondary_phone": "2378478342",
                "discounted_price": "245.70",
            },
        }

        response = self.client.post(url, data, format="json")

        # Expecting a validation error due to invalid phone number
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_merchant_member_missing_merchant_membership_fields(self):
        url = f"/api/merchants/{self.merchant.id}/members/"

        # Omitting the required field 'actual_price' from the merchant membership
        data = {
            "user": {"email": "test@gmail.com", "first_name": "testuser"},
            "cnic": "3130325676738",  # Correct CNIC
            "roles": {"role": "Customer"},
            "primary_phone": "2378478342",
            "merchant_memberships": {
                "area": "test-area",
                "city": "test_city",
                "picture": "string",
                "address": "string",
                "is_active": True,
                "meta_data": "string",
                "is_monthly": True,
                "secondary_phone": "2378478342",
                "discounted_price": "245.70",
            },
        }

        response = self.client.post(url, data, format="json")

        # Expecting a validation error due to missing 'actual_price' in merchant_memberships
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_merchant_member_unauthorized(self):
        # Create a new user without authentication
        unauthorized_client = APIClient()

        url = f"/api/merchants/{self.merchant.id}/members/"

        # Attempt to create merchant member without authentication
        data = {
            "user": {"email": "unauthorized@test.com", "first_name": "testuser"},
            "cnic": "3130325676738",  # Correct CNIC
            "roles": {"role": "Customer"},
            "primary_phone": "2378478342",
            "merchant_memberships": {
                "area": "test-area",
                "city": "test_city",
                "picture": "string",
                "address": "string",
                "is_active": True,
                "meta_data": "string",
                "is_monthly": True,
                "actual_price": "276",
                "secondary_phone": "2378478342",
                "discounted_price": "245.70",
            },
        }

        response = unauthorized_client.post(url, data, format="json")
     

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_merchant_member_duplicate_primary_phone(self):
        url = f"/api/merchants/{self.merchant.id}/members/"

        # Data 1: First POST with primary phone
        data1 = {
            "user": {
                "email": "testuser1@example.com",  # Same email as the initial user
                "first_name": "TestUser1",
            },
            "cnic": "3130325676738",  # Correct CNIC
            "roles": {"role": "Customer"},
            "primary_phone": "9876543287",  # Same primary phone as the initial user
            "merchant_memberships": {
                "area": "test-area",
                "city": "test_city",
                "picture": "string",
                "address": "string",
                "is_active": True,
                "meta_data": "string",
                "is_monthly": True,
                "actual_price": "276",
                "secondary_phone": "2378478342",
                "discounted_price": "245.70",
            },
        }

        # First post with data1
        response1 = self.client.post(url, data1, format="json")

        # Check that the response returns the correct status code
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # Data 2: Second POST with the same primary phone
        data2 = {
            "user": {
                "email": "testuser2@example.com",  # New email
                "first_name": "TestUser2",
            },
            "cnic": "3130325676738",  # Correct CNIC
            "roles": {"role": "Customer"},
            "primary_phone": "9876543287",  # Same primary phone
            "merchant_memberships": {
                "area": "test-area",
                "city": "test_city",
                "picture": "string",
                "address": "string",
                "is_active": True,
                "meta_data": "string",
                "is_monthly": True,
                "actual_price": "276",
                "secondary_phone": "2378478342",
                "discounted_price": "245.70",
            },
        }

        # Second post with data2
        response2 = self.client.post(url, data2, format="json")

        # Check that the response returns the existing data (same primary phone)
        self.assertEqual(
            response2.status_code, status.HTTP_201_CREATED
        )  # Assuming returning existing data
        self.assertEqual(response2.data["primary_phone"], "9876543287")
        self.assertEqual(
            response2.data["user"]["email"], "testuser1@example.com"
        )  # Should return the first user's email

    def test_create_merchant_member_duplicate_email(self):
        url = f"/api/merchants/{self.merchant.id}/members/"

        # Data 1: First POST with email testuser1@example.com
        data1 = {
            "user": {"email": "testuser1@example.com", "first_name": "TestUser1"},
            "cnic": "3130325676738",
            "roles": {"role": "Customer"},
            "primary_phone": "9876543287",
            "merchant_memberships": {
                "area": "test-area",
                "city": "test_city",
                "picture": "string",
                "address": "string",
                "is_active": True,
                "meta_data": "string",
                "is_monthly": True,
                "actual_price": "276",
                "secondary_phone": "2378478342",
                "discounted_price": "245.70",
            },
        }

        # First post with data1
        response1 = self.client.post(url, data1, format="json")
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # Data 2: Second POST with same email but a different primary phone
        data2 = {
            "user": {
                "email": "testuser1@example.com",  # Same email as data1
                "first_name": "TestUser2",
            },
            "cnic": "3130325676738",
            "roles": {"role": "Customer"},
            "primary_phone": "1234567890",  # New primary phone
            "merchant_memberships": {
                "area": "test-area",
                "city": "test_city",
                "picture": "string",
                "address": "string",
                "is_active": True,
                "meta_data": "string",
                "is_monthly": True,
                "actual_price": "276",
                "secondary_phone": "2378478342",
                "discounted_price": "245.70",
            },
        }

        # Second post with data2
        response2 = self.client.post(url, data2, format="json")

        # Check that the response returns a validation error for duplicate email
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "email", response2.data["user"]
        )  # Check email error inside 'user'
        self.assertEqual(response2.data["user"]["email"][0], "Email already exist.")



    def test_create_merchant_member_missing_user_details(self):
        """Test creating a merchant member without a user object"""
        url = f"/api/merchants/{self.merchant.id}/members/"
        data = {
            "cnic": "3130325676738",
            "roles": {"role": "Customer"},
            "primary_phone": "2378478342",
            "merchant_memberships": {
                "area": "test-area",
                "city": "test_city",
                "picture": "string",
                "address": "string",
                "is_active": True,
                "meta_data": "string",
                "is_monthly": True,
                "actual_price": "276",
                "secondary_phone": "2378478342",
                "discounted_price": "245.70",
            },
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_merchant_member_missing_merchant_memberships(self):
        """Test creating a merchant member without the merchant_memberships section"""
        url = f"/api/merchants/{self.merchant.id}/members/"
        data = {
            "user": {"email": "testuser@example.com", "first_name": "testuser"},
            "cnic": "3130325676738",
            "roles": {"role": "Customer"},
            "primary_phone": "2378478342",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_merchant_member_with_nonexistent_merchant(self):
        """Test creating a merchant member with a non-existent merchant ID"""
        url = f"/api/merchants/999999/members/"
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_merchant_member_with_negative_discounted_price(self):
        """Test creating a merchant member with a negative discounted_price"""
        url = f"/api/merchants/{self.merchant.id}/members/"
        data = {
            "user": {"email": "testuser@example.com", "first_name": "testuser"},
            "cnic": "3130325676738",
            "roles": {"role": "Customer"},
            "primary_phone": "2378478342",
            "merchant_memberships": {
                "area": "test-area",
                "city": "test_city",
                "picture": "string",
                "address": "string",
                "is_active": True,
                "meta_data": "string",
                "is_monthly": True,
                "actual_price": "276",
                "secondary_phone": "2378478342",
                "discounted_price": "-10.00",  # Negative value
            },
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



    def test_create_merchant_member_invalid_email(self):
        url = f"/api/merchants/{self.merchant.id}/members/"

        # Invalid email format
        data = {
            "user": {
                "email": "invalid-email",  # Invalid email
                "first_name": "testuser",
            },
            "cnic": "3130325676738",  # Valid CNIC
            "roles": {"role": "Customer"},
            "primary_phone": "2378478342",
            "merchant_memberships": {
                "area": "test-area",
                "city": "test_city",
                "picture": "string",
                "address": "string",
                "is_active": True,
                "meta_data": "string",
                "is_monthly": True,
                "actual_price": "276",
                "secondary_phone": "2378478342",
                "discounted_price": "245.70",
            },
        }

        response = self.client.post(url, data, format="json")

        # Expecting a validation error due to invalid email
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Correct assertion path
        self.assertIn("email", response.data["user"])
        self.assertEqual(
            response.data["user"]["email"][0], "Enter a valid email address."
        )

    def test_create_merchant_member_unauthorized(self):
       
        self.client.logout()
        url = f"/api/merchants/{self.merchant.id}/members/"
        data = {
            "user": {
                "email": "newuser@example.com",
                "password": "password123"
            },
           "merchant_memberships": {
                "area": "test-area",
                "city": "test_city",
                "picture": "string",
                "address": "string",
                "is_active": True,
                "meta_data": "string",
                "is_monthly": True,
                "actual_price": "276",
                "secondary_phone": "2378478342",
                "discounted_price": "245.70",
            },
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 401)  # Unauthorized
    
    def test_create_merchant_member_empty_merchant_memberships(self):
        url = f"/api/merchants/{self.merchant.id}/members/"

        data = {
            "user": {
                "email": "newuser@example.com",
                "password": "password123"
            },
            "merchant_memberships": [],  # Empty list
            "roles": {"role": "Staff"},
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)  # Bad Request if memberships cannot be empty
        self.assertIn("merchant_memberships", response.data)  # Ensure error mentions merchant_memberships

    def test_create_staff(self):
        url = f"/api/merchants/{self.merchant.id}/members/"
        staff_data = {
            "user": {"email": "testuser2@example.com", "first_name": "Jane"},
            "cnic": "3130325676739",
            "roles": {"role": "Staff"},
            "primary_phone": "1234567890",
            "merchant": self.merchant.id,  # Staff should have merchant, NOT memberships
        }

        response = self.client.post(url, staff_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"]["email"], "testuser2@example.com")

    def test_create_duplicate_staff_data(self):
        url = f"/api/merchants/{self.merchant.id}/members/"

        staff_data1 = {
            "user": {"email": "testuser2@example.com", "first_name": "Jane"},
            "cnic": "3130325676739",
            "roles": {"role": "Staff"},
            "primary_phone": "1234567890",
            "merchant": self.merchant.id,  # Staff should have merchant, NOT memberships
        }

        staff_data2 = {
            "user": {"email": "testuser2@example.com", "first_name": "Jane"},
            "cnic": "3130325676739",
            "roles": {"role": "Staff"},
            "primary_phone": "1234567891",
            "merchant": self.merchant.id,  # Staff should have merchant, NOT memberships
        }


        response1 = self.client.post(url, staff_data1, format="json")

        # First request should succeed
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        response2 = self.client.post(url, staff_data2, format="json")

        # Second request should fail due to duplicate email
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

        # Ensure the error message mentions email duplication
        self.assertIn("user", response2.data)
        self.assertIn("email", str(response2.data["user"]))

    # --------------------LISTING OF MEMBERS USING THIS API----------------------------------------------

    def test_list_merchant_members(self):
        url = f"/api/merchants/{self.merchant.id}/members/"

        # Sample data for a Customer
        member_data1 = {
            "user": {"email": "testuser1@example.com", "first_name": "John"},
            "cnic": "3130325676738",
            "roles": {"role": "Customer"},
            "primary_phone": "2378478342",
            "merchant_memberships": {
                "area": "test-area",
                "city": "test_city",
                "picture": "string",
                "address": "string",
                "is_active": True,
                "meta_data": "string",
                "is_monthly": True,
                "actual_price": "276",
                "secondary_phone": "2378478342",
                "discounted_price": "245.70",
            },
        }

        # Sample data for a Staff member
        member_data2 = {
            "user": {"email": "testuser2@example.com", "first_name": "Jane"},
            "cnic": "3130325676739",
            "roles": {"role": "Staff"},
            "primary_phone": "1234567890",
            "merchant": self.merchant.id,  # Staff should have merchant, NOT memberships
        }

        # Post both Customer and Staff members
        self.client.post(url, member_data1, format="json")
        self.client.post(url, member_data2, format="json")

        # Fetch the list of members
        response = self.client.get(url, format="json")

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)  # Ensure pagination key exists
        self.assertIsInstance(response.data["results"], list)
        self.assertGreaterEqual(
            len(response.data["results"]), 1
        )  # At least 1 customer should exist

        # Validate posted data
        emails = {user["user"]["email"] for user in response.data["results"]}

        # Customer should be present
        self.assertIn("testuser1@example.com", emails)

        # Staff should NOT be present
        self.assertNotIn("testuser2@example.com", emails)

    #---------------------------------------Filterning------------------------------
    def test_filter_merchant_members_by_role(self):
        """Test filtering merchant members by role"""
        url = f"/api/merchants/{self.merchant.id}/members/"

        # Create a Customer member
        member_data1 = {
            "user": {"email": "customer@example.com", "first_name": "Customer"},
            "cnic": "3130325676738",
            "roles": {"role": "Customer"},
            "primary_phone": "2378478342",
            "merchant_memberships": {
                "area": "test-area",
                "city": "test_city",
                "picture": "string",
                "address": "string",
                "is_active": True,
                "meta_data": "string",
                "is_monthly": True,
                "actual_price": "276",
                "secondary_phone": "2378478342",
                "discounted_price": "245.70",
            },
        }

        # Create a Staff member
        member_data2 = {
            "user": {"email": "staff@example.com", "first_name": "Staff"},
            "cnic": "3130325676739",
            "roles": {"role": "Staff"},
            "primary_phone": "1234567890",
            "merchant": self.merchant.id,
        }

        self.client.post(url, member_data1, format="json")
        self.client.post(url, member_data2, format="json")

        # Filter members by role 'Customer'
        response = self.client.get(f"{url}?role=Customer", format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 1)
        print('respinse of customer',response.data)

        emails = {user["user"]["email"] for user in response.data["results"]}
        self.assertIn("customer@example.com", emails)
        self.assertNotIn("staff@example.com", emails)

        # Filter members by role 'Staff'
        response = self.client.get(f"{url}?role=Staff", format="json")
        print('respinse of staff',response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 1)
        emails = {user["user"]["email"] for user in response.data["results"]}
        self.assertIn("staff@example.com", emails)
        self.assertNotIn("customer@example.com", emails)
    def test_filter_merchant_members_by_first_name(self):
        """Test filtering merchant members by first name"""
        url = f"/api/merchants/{self.merchant.id}/members/"

        # Create a member
        member_data = {
            "user": {"email": "searchuser@example.com", "first_name": "SearchUser"},
            "cnic": "3130325676740",
            "roles": {"role": "Customer"},
            "primary_phone": "2378418342",
            "merchant_memberships": {
                "area": "test-area",
                "city": "test_city",
                "picture": "string",
                "address": "string",
                "is_active": True,
                "meta_data": "string",
                "is_monthly": True,
                "actual_price": "276",
                "secondary_phone": "2378478342",
                "discounted_price": "245.70",
            },
        }

        self.client.post(url, member_data, format="json")

        # Filter members by first name
        response = self.client.get(f"{url}?user__first_name=SearchUser", format="json")
        print('ressssssssssssssssssssss', response.data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 1)
        
        first_names = {user["user"]["first_name"] for user in response.data["results"]}
        self.assertIn("SearchUser", first_names)

    def test_filter_merchant_members_by_city(self):
        """Test filtering merchant members by city"""
        url = f"/api/merchants/{self.merchant.id}/members/"

        # Create a member in a specific city
        member_data = {
            "user": {"email": "cityuser@example.com", "first_name": "CityUser"},
            "cnic": "3130325676741",
            "roles": {"role": "Customer"},
            "primary_phone": "2378478342",
            "merchant_memberships": {
                "area": "test-area",
                "city": "Lahore",
                "picture": "string",
                "address": "string",
                "is_active": True,
                "meta_data": "string",
                "is_monthly": True,
                "actual_price": "276",
                "secondary_phone": "2378478342",
                "discounted_price": "245.70",
            },
        }

        self.client.post(url, member_data, format="json")

        # Filter members by city 'Lahore'
        response = self.client.get(f"{url}?city=Lahore", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 1)
        cities = {user["merchant_memberships"]["city"] for user in response.data["results"]}
        self.assertIn("Lahore", cities)
