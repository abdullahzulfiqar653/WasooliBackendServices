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

from services.s3 import S3Service

s3_client = S3Service()


class MerchantMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)
    primary_phone = serializers.CharField(validators=[])
    primary_image = serializers.ImageField(required=False, allow_null=True)
    roles = MemberRoleSerializer(required=True, write_only=True)

    class Meta:
        model = MerchantMember
        fields = [
            "id",
            "user",
            "cnic",
            "code",
            "roles",
            "picture",
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

        fake_view = getattr(self.context.get("view"), "swagger_fake_view", False)
        if fake_view:
            self.fields[membership] = MerchantMembershipSerializer()
        else:
            if request.method == "GET":
                self.fields[membership] = serializers.SerializerMethodField()
            if request.method in ("POST", "PUT", "PATCH"):
                self.fields[membership] = MerchantMembershipSerializer(
                    required=True, write_only=True, allow_null=True
                )
            if request.method in ("PUT", "PATCH"):
                self.fields["roles"] = MemberRoleSerializer(
                    required=False, write_only=True, allow_null=True
                )
                # Pass the member instance in the context so the UserSerializer can access the associated user
                self.context["member"] = self.instance
                self.fields["user"] = UserSerializer(required=True)

        if request.method == "POST":
            role_data = request.data.get("roles", {})
            role = role_data.get("role")
            if role == RoleChoices.STAFF:
                self.fields[membership].required = False

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

        if self.instance:
            if value is None or self.instance.primary_phone == value:
                return self.instance.primary_phone

            queryset = MerchantMember.objects.filter(primary_phone=value)
            if queryset.exclude(id=self.instance.id).exists():
                raise serializers.ValidationError(
                    "This phone number is already in use by another user."
                )
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
        primary_image = validated_data.pop("primary_image", None)
        merchant_memberships_data = validated_data.pop("merchant_memberships", None)

        queryset = MerchantMember.objects.filter(primary_phone=primary_phone)

        if queryset.exists():
            member = queryset.first()
            if roles_data["role"] == RoleChoices.STAFF:
                member.merchant = merchant
                member.save()
        else:
            user = User.objects.create(
                **user_data,
                username=f"{user_data['first_name']}_{secrets.token_hex(10)}",
            )
            user.set_password(secrets.token_hex(7))
            if roles_data["role"] == RoleChoices.STAFF:
                validated_data["merchant"] = merchant
            member = MerchantMember.objects.create(user=user, **validated_data)

            if primary_image:
                name = primary_image.name.replace(" ", "_")
                s3_key = f"profile/primary/{member.id}/{name}"
                s3_url = s3_client.upload_file(primary_image, s3_key)
                member.picture = s3_url
                member.save()

        roles = MemberRole.objects.filter(member=member, role=roles_data["role"])
        if not roles.exists():
            # Create MerchantMemberRole object
            MemberRole.objects.create(member=member, **roles_data)

        if roles_data["role"] == RoleChoices.CUSTOMER:
            # Add the 'member' field to the MerchantMembership data (it references MerchantMember)
            merchant_memberships_data["member"] = member
            merchant_memberships_data["merchant"] = merchant
            secondary_image = merchant_memberships_data.pop("secondary_image", None)
            membership = MerchantMembership.objects.filter(
                member=member, merchant=merchant
            )
            if not membership.exists():
                membership = MerchantMembership.objects.create(
                    **merchant_memberships_data
                )
            if secondary_image:
                name = secondary_image.name.replace(" ", "_")
                s3_key = f"wasooli/profile/secondary/{member.id}/{name}"
                s3_url = s3_client.upload_file(secondary_image, s3_key)
                membership.picture = s3_url
                membership.save()

        return member

    def update(self, instance, validated_data):
        request = self.context.get("request")
        validated_data.pop("roles", None)
        user_data = validated_data.pop("user")
        primary_image = validated_data.pop("primary_image", None)
        memberships = validated_data.pop("merchant_memberships", None)
        if user_data:
            if user_data.get("email"):
                instance.user.email = user_data.email
            instance.user.first_name = user_data.get(
                "first_name", instance.user.first_name
            )
            instance.user.save()

        if primary_image:
            name = primary_image.name.replace(" ", "_")
            s3_key = f"profile/primary/{instance.id}/{name}"
            s3_url = s3_client.upload_file(primary_image, s3_key)
            validated_data["picture"] = s3_url

        if memberships:
            queryset = MerchantMembership.objects.filter(
                member=instance, merchant=request.merchant
            )
            if queryset.exists():
                membership = queryset.first()
                secondary_image = memberships.pop("secondary_image", None)
                # Fields to be updated
                fields_to_update = [
                    "area",
                    "city",
                    "address",
                    "is_active",
                    "meta_data",
                    "is_monthly",
                    "actual_price",
                    "secondary_phone",
                    "discounted_price",
                ]
                for field in fields_to_update:
                    setattr(
                        membership,
                        field,
                        memberships.get(field, getattr(membership, field)),
                    )

                if secondary_image:
                    name = secondary_image.name.replace(" ", "_")
                    s3_key = f"wasooli/profile/secondary/{instance.id}/{name}"
                    s3_url = s3_client.upload_file(secondary_image, s3_key)
                    membership.picture = s3_url
                membership.save()
        return super().update(instance, validated_data)
