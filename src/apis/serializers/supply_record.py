from rest_framework import serializers
from apis.models.supply_record import SupplyRecord


class SupplyRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplyRecord
        fields = [
            "id",
            "given",
            "taken",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        validated_data["merchant_membership"] = self.context["request"].membership
        return super().create(validated_data)
