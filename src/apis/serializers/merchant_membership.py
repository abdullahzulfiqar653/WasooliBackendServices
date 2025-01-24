import re
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, ValidationError

from apis.models.lookup import Lookup
from apis.models.merchant_membership import MerchantMembership

from services.s3 import S3Service

s3_client = S3Service()


class MerchantMembershipSerializer(ModelSerializer):
    meta_data = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = MerchantMembership
        fields = [
            "area",
            "city",
            "picture",
            "address",
            "merchant",
            "is_active",
            "meta_data",
            "is_monthly",
            "actual_price",
            "secondary_phone",
            "discounted_price",
        ]
        read_only_fields = ["account", "merchant"]
        extra_kwargs = {
            "is_active": {"required": True},
            "is_monthly": {"required": True},
        }

    def validate(self, data):
        if "actual_price" in data and "discounted_price" in data:
            if data["discounted_price"] > data["actual_price"]:
                raise ValidationError(
                    {
                        "discounted_price": "Discounted price cannot be larger than the actual price."
                    }
                )
        city = data.get("city", "").strip().lower()
        area = data.get("area", "").strip().lower()

        if not city:
            raise ValidationError({"city": "City is required"})
        if not area:
            raise ValidationError({"area": "Area is required"})

        if city.replace(" ", "").isdigit():
            raise ValidationError({"city": "City cannot be a number."})

        if area.replace(" ", "").isdigit():
            raise ValidationError({"area": "Area cannot be a number."})

        # 'city' is the type name for cities
        type = Lookup.objects.get(name="city")  # Ensure this exists as a city type
        city_type = None
        if not Lookup.objects.filter(name=city, type=type).exists():
            city_type = Lookup.objects.create(name=city, type=type)
        else:
            city_type = Lookup.objects.filter(name=city, type=type).first()

        if not Lookup.objects.filter(name=area, type_id=city_type.id).exists():
            Lookup.objects.create(name=area, type=city_type)
        return data

    def validate_actual_price(self, value):
        """Ensure that the actual price is not negative."""
        if value < 0:
            raise ValidationError("Actual price cannot be negative.")
        return value

    def validate_discounted_price(self, value):
        """Ensure that the discounted price is not negative."""
        if value < 0:
            raise ValidationError("Discounted price cannot be negative.")
        return value

    def validate_picture(self, value):
        if value:
            value = s3_client.make_presigned_file_public(value)
            if value is None:
                raise serializers.ValidationError(
                    "You have passed wrong s3_key in picture attribute."
                )
        return value

    def validate_secondary_phone(self, value):
        if value:
            if not re.match(r"^\d{10}$", value):
                raise serializers.ValidationError(
                    "Primary phone must be exactly 10 digits long and numeric."
                )
            if value.strip().startswith("0"):
                raise ValidationError("Contact number cannot start with '0'.")
        return value
