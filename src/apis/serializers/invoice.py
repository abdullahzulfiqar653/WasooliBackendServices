from rest_framework import serializers
from apis.models.invoice import Invoice
from apis.models.transaction_history import TransactionHistory


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        exclude = ["is_user_invoice", "member", "updated_at"]
        read_only_fields = [
            "status",
            "member",
            "is_monthly",
            "handled_by",
            "due_amount",
        ]

    def validate_total_amount(self, value):
        if value < 0:
            raise serializers.ValidationError("Amount cannot be less then 0.")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["member"] = request.member
        validated_data["is_monthly"] = False
        invoice = super().create(validated_data)
        merchant_membership = request.merchant.members.filter(
            member=request.member
        ).first()
        TransactionHistory.objects.create(
            invoice=invoice,
            metadata={"invoices": [invoice.code]},
            merchant_membership=merchant_membership,
            is_online=False,
            debit=invoice.total_amount,
            type=TransactionHistory.TYPES.BILLING,
            transaction_type=TransactionHistory.TRANSACTION_TYPE.DEBIT,
        )
        return invoice

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
