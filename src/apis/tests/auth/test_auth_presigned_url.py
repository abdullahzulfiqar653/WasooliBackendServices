from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apis.models.merchant import Merchant
from apis.models.merchant_member import MerchantMember
from apis.models.member_role import MemberRole, RoleChoices
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

User = get_user_model()


class TestPreSignedUrlCreateAPIView(TestCase):
    def setUp(self):
        """Set up test data for PreSignedUrl API"""
        self.client = APIClient()

        # Create test user (Merchant)
        self.user = User.objects.create_user(
            email="merchant@gmail.com",
            password="testpassword",
            username="merchant_user",
        )

        # Create a merchant
        self.merchant = Merchant.objects.create(
            name="Test Merchant",
            type="Retail",
            area="Test Area",
            city="Test City",
            is_advance_payment=True,
            owner=self.user,
        )

        # Create a merchant member
        self.merchant_member = MerchantMember.objects.create(
            user=self.user,
            merchant=self.merchant,
            primary_phone="3123456789",
            code="1234",
        )

        # Assign a merchant role
        self.role = MemberRole.objects.create(
            member=self.merchant_member, role=RoleChoices.MERCHANT
        )

        # Authenticate user
        self.client.force_authenticate(user=self.user)

        # API endpoint
        self.url = "/api/auth/presigned-url/"

    def generate_valid_image(self):
        """Generate a valid image file"""
        image = Image.new("RGB", (100, 100), "white")  # ✅ Create a valid image
        image_io = BytesIO()
        image.save(image_io, format="JPEG")  # ✅ Save image as valid JPEG
        image_io.seek(0)
        return SimpleUploadedFile(
            "test_image.jpg", image_io.getvalue(), content_type="image/jpeg"
        )

    def test_presigned_url_creation_success(self):
        """Test that a pre-signed URL is generated successfully"""

        file_data = self.generate_valid_image()  # ✅ Use valid image

        response = self.client.post(
            self.url,
            {"file": file_data, "public": "true"},
            format="multipart",
        )

        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_presigned_url_unauthorized(self):
        """Test that an unauthenticated user cannot generate a pre-signed URL"""
        self.client.logout()  # Log out user
        data = {"file": "testfile.png", "public": True}
        response = self.client.post(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
