import io
import csv
import secrets
from rest_framework import serializers
from django.contrib.auth.models import User
from apis.models.merchant_member import MerchantMember
from apis.models.member_role import MemberRole, RoleChoices

from apis.models.merchant_membership import MerchantMembership

class BulkCustomerSerializer(serializers.Serializer):
    file = serializers.FileField()

    def create(self, validated_data):
        request = self.context.get("request")
        if "file" not in validated_data:
            raise serializers.ValidationError({"file": "No file was provided"})

        uploaded_file = validated_data["file"]

        try:
            decoded_file = io.StringIO(uploaded_file.read().decode("utf-8"))
            csv_reader = csv.DictReader(decoded_file)

            users, roles, members, memberships = [], [], [], []
            last_MerchantMembership = MerchantMembership.objects.order_by("-id").first()
            last_account = (
                int(last_MerchantMembership.account)
                if last_MerchantMembership and last_MerchantMembership.account.isdigit()
                else 0
            )
            last_member = MerchantMember.objects.order_by("-id").first()
            last_code = (
                int(last_member.code)
                if last_member and last_member.code.isdigit()
                else 0
            )
            for row in csv_reader:
                first_name = row.get("first_name", "").strip()
                primary_phone = row.get("primary_phone", "").strip()
                area = row.get("area", "").strip()
                city = row.get("city", "").strip()

                if not first_name or not primary_phone or not area or not city:
                    continue

                if not primary_phone.startswith("3") or len(primary_phone) != 10:
                    continue

                member_is = MerchantMember.objects.filter(
                    primary_phone=primary_phone
                ).first()

                if not member_is:

                    user = User(
                        first_name=first_name,
                        email=row.get("email", "").strip(),
                        password=secrets.token_hex(7),
                        username=f"{first_name}_{secrets.token_hex(5)}",
                    )
                    users.append(user)
                    last_code += 1
                    member = MerchantMember(
                        user=user,
                        merchant=request.merchant,
                        primary_phone=primary_phone,
                        code=str(last_code),
                        id=f"{MerchantMember.UID_PREFIX}{secrets.token_hex(6)}",
                    )

                    members.append(member)
                    role = MemberRole(
                        member=member,
                        role=RoleChoices.CUSTOMER,
                        id=f"{MemberRole.UID_PREFIX}{secrets.token_hex(6)}",
                    )

                    roles.append(role)
                    last_account += 1
                    membership = MerchantMembership(
                        member=member,
                        area=area,
                        city=city,
                        actual_price=row.get("actual_price", "0.00").strip(),
                        merchant_id=request.merchant.id,
                        discounted_price=row.get("discounted_price", "0.00").strip(),
                        account=str(last_account),
                        id=f"{MerchantMembership.UID_PREFIX}{secrets.token_hex(6)}",
                    )
                    memberships.append(membership)
                else:
                    last_account += 1
                    membership = MerchantMembership(
                        member=member_is,
                        area=area,
                        city=city,
                        actual_price=row.get("actual_price", "0.00").strip(),
                        merchant_id=request.merchant.id,
                        discounted_price=row.get("discounted_price", "0.00").strip(),
                        account=str(last_account),
                        id=f"{MerchantMembership.UID_PREFIX}{secrets.token_hex(6)}",
                    )
                    memberships.append(membership)

            User.objects.bulk_create(users)
            MerchantMember.objects.bulk_create(members)
            MemberRole.objects.bulk_create(roles)
            MerchantMembership.objects.bulk_create(memberships)

            return {"message": "Users imported successfully"}

        except Exception as e:
            raise serializers.ValidationError({"error": [str(e)]})
