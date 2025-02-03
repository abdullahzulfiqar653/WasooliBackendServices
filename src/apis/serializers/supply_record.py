from django.utils import timezone
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
        request = self.context["request"]
        member_ship = request.membership

        # Get today's date
        today = timezone.now().date()

        # Try to retrieve an existing supply record for today
        supply_record, created = SupplyRecord.objects.get_or_create(
            merchant_membership=member_ship,
            created_at__date=today,  # Filter to get record for the current day
            defaults=validated_data,  # Defaults used only if a new object is created
        )

        if not created:
            # If found, update the existing record
            for key, value in validated_data.items():
                setattr(supply_record, key, value)
            supply_record.save()

        return supply_record
