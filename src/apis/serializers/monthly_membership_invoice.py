from rest_framework import serializers


class MonthlyMembershipInvoiceSerializer(serializers.Serializer):
    # class Meta:
    #     fields = []

    def create(self, validated_data):
        return super().create(validated_data)
