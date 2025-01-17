import re
import secrets
from rest_framework import serializers
from django.contrib.auth.models import User

from apis.models.merchant_member import MerchantMember
from apis.models.member_role import MemberRole, RoleChoices
from apis.models.merchant_membership import MerchantMembership

from apis.serializers.user import UserSerializer
from apis.serializers.member_role import MemberRoleSerializer
from apis.serializers.merchant_membership import MerchantMembershipSerializer


class MerchantMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)
    primary_phone = serializers.CharField(validators=[])
    primary_image = serializers.ImageField(required=False)
    roles = MemberRoleSerializer(required=True, write_only=True)
    area = serializers.CharField(source="area_name", read_only=True)
    is_active = serializers.BooleanField(source="current_active", read_only=True)

    class Meta:
        model = MerchantMember
        fields = [
            "id",
            "user",
            "cnic",
            "code",
            "area",
            "roles",
            "picture",
            "is_active",
            "primary_phone",
            "primary_image",
            "merchant_memberships",
        ]
        extra_kwargs = {
            "cnic": {"required": False},
            "picture": {"required": False},
        }
        read_only_fields = ["picture"]

    def __init__(self, *args, **kwargs):
        membership = "merchant_memberships"
        super(MerchantMemberSerializer, self).__init__(*args, **kwargs)
        # Adjust the 'required' attribute of merchant_memberships based on the role data if present
        request = self.context.get("request")
        if request and "roles" in request.data:
            role_data = request.data["roles"]
            role = role_data.get("role")
            if role == RoleChoices.STAFF:
                self.fields[membership].required = False

        fake_view = getattr(self.context.get("view"), "swagger_fake_view", False)
        if fake_view:
            self.fields[membership] = MerchantMembershipSerializer()
        else:
            if request.method == "GET":
                self.fields[membership] = serializers.SerializerMethodField()
            if request.method == "POST":
                self.fields[membership] = MerchantMembershipSerializer(
                    required=True, write_only=True
                )

    def get_merchant_memberships(self, obj) -> dict:
        request = self.context.get("request")
        membership = MerchantMembership.objects.filter(
            member=obj, merchant=request.merchant
        ).first()

        if membership:
            return MerchantMembershipSerializer(membership).data
        return {}

    def validate_cnic(self, value):
        if value and not re.match(r"^\d{13}$", value):
            raise serializers.ValidationError(
                "CNIC must be exactly 13 digits long and numeric."
            )
        return value

    def validate_primary_phone(self, value):
        if not re.match(r"^\d{10}$", value):
            raise serializers.ValidationError(
                "Primary phone must be exactly 10 digits long and numeric."
            )
        if value.strip().startswith("0"):
            raise serializers.ValidationError("Contact number cannot start with '0'.")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        """
        Handle the creation of both MerchantMember and MerchantMembership objects.
        """
        merchant = request.merchant
        user_data = validated_data.pop("user")
        roles_data = validated_data.pop("roles")
        primary_phone = validated_data["primary_phone"]
        if "merchant_memberships" in validated_data:
            merchant_memberships_data = validated_data.pop("merchant_memberships")

        queryset = MerchantMember.objects.filter(primary_phone=primary_phone)

        if queryset.exists():
            member = queryset.first()
            if roles_data["role"] == RoleChoices.STAFF:
                member.merchant = merchant
                member.save()
        else:
            user = User.objects.create(**user_data, username=primary_phone)
            user.set_password(secrets.token_hex(7))
            if roles_data["role"] == RoleChoices.STAFF:
                validated_data["merchant"] = merchant
            member = MerchantMember.objects.create(user=user, **validated_data)

        roles = MemberRole.objects.filter(member=member, role=roles_data["role"])
        if not roles.exists():
            # Create MerchantMemberRole object
            MemberRole.objects.create(member=member, **roles_data)

        if roles_data["role"] == RoleChoices.CUSTOMER:
            # Add the 'member' field to the MerchantMembership data (it references MerchantMember)
            merchant_memberships_data["member"] = member
            merchant_memberships_data["merchant"] = merchant

            # Create the MerchantMembership object
            membership = MerchantMembership.objects.filter(
                member=member, merchant=merchant
            )
            if not membership.exists():
                MerchantMembership.objects.create(**merchant_memberships_data)

        return member
