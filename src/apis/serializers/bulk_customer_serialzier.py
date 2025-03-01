import csv
import secrets
from io import TextIOWrapper
from rest_framework import status
from rest_framework import serializers
from django.contrib.auth.models import User
from apis.models.merchant_member import MerchantMember
from apis.models.member_role import MemberRole, RoleChoices

from apis.models.merchant_membership import MerchantMembership


class BulkCustomerSerializer(serializers.Serializer):
    file = serializers.FileField()

    def create(self, validated_data):
        request = self.context.get("request")
        uploaded_file = validated_data["file"]
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
                # primary_phone should start with 3 and exactly 10 diits
                if not primary_phone.startswith("3") or len(primary_phone) > 0:
                    continue

                member = MerchantMember.objects.filter(
                    primary_phone=primary_phone
                ).first()
                users = []
                roles = []
                members = []
                memberships = []
                if not member:
                    user = User(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password=secrets.token_hex(7),
                        username=f"{first_name}_{secrets.token_hex(5)}",
                    )
                    users.append(user)
                    member = MerchantMember(
                        user=user,
                        primary_phone=primary_phone,
                        id=f"{MerchantMember.UID_PREFIX}{secrets.token_hex(6)}",
                    )
                    members.append(member)
                    role = MemberRole(
                        member=member,
                        role=RoleChoices.CUSTOMER,
                        id=f"{MemberRole.UID_PREFIX}{secrets.token_hex(6)}",
                    )
                    roles.append(role)
                    membership = MerchantMembership(
                        member=member,
                        area=area,
                        city=city,
                        actual_price=actual_price,
                        merchant_id=request.merchent,
                        discounted_price=discounted_price,
                        id=f"{MerchantMembership.UID_PREFIX}{secrets.token_hex(6)}",
                    )
                    memberships.append(membership)
            User.objects.bulk_create(users)
            MemberRole.objects.bulk_create(roles)
            MerchantMember.objects.bulk_create(members)
            MerchantMembership.objects.bulk_create(memberships)

            return {"message": "Users imported successfully"}

        except Exception as e:
            raise serializers.ValidationError(
                {"error": [str(e)]}, status=status.HTTP_400_BAD_REQUEST
            )
