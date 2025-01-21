from rest_framework import serializers
from apis.models.invoice import Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        exclude = ["is_user_invoice"]
        read_only_fields = [
            "member",
            "is_monthly",
            "handled_by",
        ]

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
