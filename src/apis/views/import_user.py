import os
import csv
import secrets
from io import TextIOWrapper

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema

from apis.models.member_role import RoleChoices
from apis.models import MerchantMember, MerchantMembership, MemberRole

from apis.serializers.csv_file_upload import CSVUploadSerializer

User = get_user_model()


@extend_schema(
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "file": {"type": "string", "format": "binary"},
            },
            "required": ["file"],
        }
    },
)
class MerchantMemberCSVUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, merchant_id, *args, **kwargs):
        file_serializer = CSVUploadSerializer(data=request.data)
        if not file_serializer.is_valid():
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response(
                {"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            decoded_file = TextIOWrapper(uploaded_file.file, encoding="utf-8")
            csv_reader = csv.DictReader(decoded_file)

            for row in csv_reader:
                first_name = row.get("first_name", "").strip()
                last_name = row.get("last_name", "").strip()
                email = row.get("email", "").strip()
                primary_phone = row.get("primary_phone", "").strip()
                area = row.get("area", "").strip()
                city = row.get("city", "").strip()
                actual_price = row.get("actual_price", "0.00").strip()
                discounted_price = row.get("discounted_price", "0.00").strip()

                if not first_name or not primary_phone or not area or not city:
                    continue

                member = MerchantMember.objects.filter(
                    primary_phone=primary_phone
                ).first()

                if not member:

                    user = User.objects.create_user(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password=secrets.token_hex(7),
                        username=f"{first_name}_{secrets.token_hex(5)}",
                    )

                    member = MerchantMember.objects.create(
                        user=user,
                        primary_phone=primary_phone,
                        merchant_id=merchant_id,
                    )

                    MemberRole.objects.create(member=member, role=RoleChoices.CUSTOMER)

                    MerchantMembership.objects.create(
                        member=member,
                        merchant_id=merchant_id,
                        area=area,
                        city=city,
                        actual_price=actual_price,
                        discounted_price=discounted_price,
                    )

            return Response(
                {"message": "Users imported successfully"},
                status=status.HTTP_201_CREATED,
            )

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
