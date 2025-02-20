from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from apis.models.merchant_member import MerchantMember
from apis.models.merchant_membership import MerchantMembership
from rest_framework.test import APIClient
from apis.models.merchant import Merchant


class MemberRetrieveTestCase(APITestCase):
    def setUp(self):
        """Set up test database with a merchant, different owner, and membership"""
        self.client = APIClient()

        self.user1 = User.objects.create_user(
            email="testmember122@gmail.com",
            password="testpassword",
            username="testuser11",
        )
        self.user2 = User.objects.create_user(
            email="testmember222@gmail.com",
            password="testpassword",
            username="testuser12",
        )

        # ✅ Create a separate user as the merchant owner
        self.owner = User.objects.create_user(
            email="owner22@gmail.com",
            password="ownerpassword",
            username="merchantowner123",
        )

        self.merchant = Merchant.objects.create(
            name="Test's Member Business",
            type="Water",
            area="Test Area",
            city="Test City",
            is_advance_payment=True,
            commission_structure={
                "cash": [{"max_credit": 1000, "commission": 0.1}],
                "online": [{"max_credit": 1000, "commission": 0.5}],
            },
            owner=self.owner, 
        )
        
        print("What is inside merchnat", self.merchant.id)
        # ✅ Create MerchantMembership and link to Merchant
        self.merchant_member1 = MerchantMember.objects.create(
            user=self.user2,  # ✅ Test user is now just a member, not the owner
            merchant=self.merchant,
            primary_phone="3124567897",
        )
   
        self.merchant_member2 = MerchantMember.objects.create(
            user=self.user1,  # ✅ Test user is now just a member, not the owner
            merchant=self.merchant,
            primary_phone="3456765432",
        )
 

        self.merchant_membership1 = MerchantMembership.objects.create(
            merchant=self.merchant,
            member=self.merchant_member1,  # or self.user2, depending on logic
            is_active=True,
            actual_price=1000,
            discounted_price=900,  # Example field
        )
        
        self.merchant.membership = self.merchant_membership1
        self.merchant.save()
       
   


        
        self.merchant_membership2 = MerchantMembership.objects.create(
            merchant=self.merchant,
            member=self.merchant_member2,  # or self.user2, depending on logic
            is_active=True,  # Example field
            actual_price=2000,
            discounted_price=1000,  # Example field
        )
        self.merchant.membership = self.merchant_membership2
       

        self.client.force_authenticate(user=self.owner)

        url = f"/api/merchants/{self.merchant.id}/members/"
    
        url2 = f"/api/merchants/{self.merchant.id}/members/?role=Staff"


        data = {
            "user": {"email": "test22@gmail.com", "first_name": "testuser22"},
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
        data1= {
            "user": {"email": "test2@gmail.com", "first_name": "testuser"},
            "cnic": "3130325676768",  # Correct CNIC
            "roles": {"role": "Staff"},  # Ensure 'member' is a valid choice
            "picture": "string",
            "primary_phone": "2378078342",  # Correct phone number
            "merchant_memberships": {
                "area": "test-area",
                "city": "test_city",
                "picture": "string",
                "address": "string",
                "is_active": True,
                "meta_data": "string",
                "is_monthly": True,
                "actual_price": "1000",  # Corrected to a positive value
                "secondary_phone": "2378478342",  # Correct phone number
                "discounted_price": "980.70",  # Corrected to a positive value
            },
        }

        response1 = self.client.post(url, data, format="json")
        response2 = self.client.post(url, data1, format="json")

        response3 = self.client.get(url)
        response4=self.client.get(url2)
        print('-----------------------------Merchant1------------------------------------')
        print(response4.data)
        print('-----------------------------Merchant1------------------------------------')



        self.member_id = response3.data["results"][0]["id"]
        self.member_id2 = response4.data["results"][0]["id"]

        self.valid_url = f"/api/members/{self.member_id}/"

        # Force authentication for the test user

    def test_retrieve_valid_member(self):
        
        response = self.client.get(self.valid_url)
        

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.member_id)

  
        self.assertEqual(response.data["user"]["email"], "test22@gmail.com")
        self.assertEqual(response.data["user"]["first_name"], "testuser22")

 
        self.assertEqual(response.data["cnic"], "3130325676738")
        self.assertEqual(response.data["primary_phone"], "2378478342")


        self.assertEqual(response.data["merchant_memberships"]["area"], "test-area")
        self.assertEqual(response.data["merchant_memberships"]["city"], "test_city")
        self.assertEqual(response.data["merchant_memberships"]["actual_price"], "276.00")
        self.assertEqual(response.data["merchant_memberships"]["discounted_price"], "245.70")


        self.assertTrue(response.data["merchant_memberships"]["is_active"])

    def test_retrieve_by_staff(self):
        url=f"/api/members/{self.member_id2}/?role='Staff"
        print('---------Staffff--------')
        response = self.client.get(url)
        print(response.data)
        print('---------Staffff--------')
        


    def test_retrieve_unauthorized(self):
        self.client.logout()
        response = self.client.get(self.valid_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
     
        # Assert the error message indicates authentication is required
        self.assertEqual(response.data["detail"], "Authentication credentials were not provided.")


    def test_retrieve_unauthenticated_or_if_id_not_present(self):
        owner2 = User.objects.create_user(
            email="owner55@gmail.com",
            password="ownerpassword2",
            username="merchantowner277",
        )
        user2 = User.objects.create_user(
            email="testmemberee@gmail.com",
            password="testpassword",
            username="testuser7711",
        )
        merchant2 = Merchant.objects.create(
            name="Test's Member Businessof Internet Merchant2" ,
            type="Internet",
            area="Test Area2",
            city="Test City2",
            is_advance_payment=True,
            commission_structure={
                "cash": [{"max_credit": 3000, "commission": 0.1}],
                "online": [{"max_credit": 1000, "commission": 0.5}],
            },
            owner=owner2, 
        )

        merchant_member2 = MerchantMember.objects.create(
            user=user2,  # ✅ Test user is now just a member, not the owner
            merchant=merchant2,
            primary_phone="31245887197",
        )

        merchant_membership2 = MerchantMembership.objects.create(
            merchant=merchant2,
            member=merchant_member2,  # or self.user2, depending on logic
            is_active=True,
            actual_price=10000,
            discounted_price=9800,  # Example field
        )
        merchant2.membership = merchant_membership2
        merchant2.save()
        self.client.logout()
        self.client.force_authenticate(user=owner2)
        url = f"/api/merchants/{merchant2.id}/members/"
        data = {
            "user": {"email": "testmerchantyfhdcb@gmail.com", "first_name": "testuserddddddcd21"},
            "cnic": "3130315676738",  # Correct CNIC
            "roles": {"role": "Customer"},  # Ensure 'member' is a valid choice
            "picture": "string",
            "primary_phone": "2300478342",  # Correct phone number
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
        response1 = self.client.post(url, data, format="json")
        print('RESPONSE OF MERCHANT 2',response1.data)
        url = f"/api/merchants/{merchant2.id}/members/"
        response = self.client.get(url)
        print('RESPONSE OF MEMBERS OF MERCHANT 2 is given below ',response.data)
        member_id = response.data["results"][0]["id"]
        valid_url = f"/api/members/{member_id}/"
        response2= self.client.get(valid_url)
        print('RESposne of requested member is given below ',response2.data)
        print('RESPONSE OF ID  OF MERCHANT ID IS ',response.data)
        
        unauthenticated_url=f"/api/members/{self.member_id}/"
        print('--------------------------Response4-------------------------------')
        response4 = self.client.get(unauthenticated_url)
        print("FULL RESPONSE OBJECT:", response4)
        print("STATUS CODE:", response4.status_code)
        print("HEADERS:", response4.headers)
        print("RESPONSE OF UNAUTHENTICATED REQUEST IS:", response4.data)
        self.assertEqual(response4.status_code, 404)
        self.assertEqual(response4.data['detail'][0], 'Matching id not found.')

    


    def test_retrieve_unauthorized(self):
        self.client.logout()
        response = self.client.get(self.valid_url)
        print(response.data)


    