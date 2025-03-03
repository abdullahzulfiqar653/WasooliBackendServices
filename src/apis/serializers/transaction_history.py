from rest_framework import serializers
from apis.models.transaction_history import TransactionHistory


class TransactionHistorySerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=9, decimal_places=2, write_only=True)

    class Meta:
        model = TransactionHistory
        fields = [
            "id",
            "amount",
            "value",
            "balance",
            "metadata",
            "is_online",
            "created_at",
            "updated_at",
            "transaction_type",
        ]
        read_only_fields = [
            "id",
            "value",
            "balance",
            "metadata",
            "is_online",
            "created_at",
            "updated_at",
            "transaction_type",
        ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value

    def create(self, validated_data):
        amount = validated_data.pop("amount")
        request = self.context.get("request")

        validated_data["value"] = amount
        validated_data["is_online"] = False
        validated_data["merchant_membership"] = request.membership
        validated_data["type"] = TransactionHistory.TYPES.BILLING
        validated_data["transaction_type"] = TransactionHistory.TRANSACTION_TYPE.CREDIT
        transaction = super().create(validated_data)
        transaction.apply_payment(request.user.first_name)
        return transaction

    def update(self, instance, validated_data):
        instance.revert_transaction()  # This deletes the instance as well
        return self.create(validated_data)
