from decimal import Decimal
from rest_framework import serializers
from apis.models.invoice import Invoice
from apis.models.transaction_history import TransactionHistory


class InvoiceSerializer(serializers.ModelSerializer):
    mark_paid = serializers.BooleanField(
        write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Invoice
        exclude = ["is_user_invoice", "member", "updated_at"]
        read_only_fields = [
            "status",
            "member",
            "mark_paid",
            "is_monthly",
            "handled_by",
            "due_amount",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method in ["PATCH", "PUT"]:
            # If it's a PATCH/PUT request, make total_amount optional and allow null
            self.fields["total_amount"].required = False
            self.fields["total_amount"].allow_null = True

    def validate_total_amount(self, value):
        if value:
            if value <= 0:
                raise serializers.ValidationError("Amount cannot be 0 or less then 0.")
        return value

    def validate_mark_paid(self, value):
        if value:
            if self.instance and self.instance.status == Invoice.STATUS.PAID:
                raise serializers.ValidationError("Invoice is already paid.")
        return value

    def validate(self, data):
        if self.instance:
            new_amount = data.get("total_amount")
            total_amount = self.instance.total_amount
            due_amount = self.instance.due_amount
            if new_amount:
                if not total_amount == new_amount:
                    if not data.get("metadata", {}).get("remarks"):
                        raise serializers.ValidationError(
                            {"detail": "Please write why you are updating the invoice."}
                        )
                if total_amount > new_amount:
                    difference = total_amount - new_amount
                    if due_amount - difference < 0:
                        raise serializers.ValidationError(
                            {"detail": "Due amount cannot be less than 0."}
                        )
        return data

    def validate_metadata(self, value):
        if value:
            if not isinstance(value, dict):
                raise serializers.ValidationError("Metadata must be a dictionary.")
        return value

    def create(self, validated_data):
        _ = validated_data.pop("mark_paid", False)
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
        request = self.context.get("request")
        mark_paid = validated_data.pop("mark_paid", False)
        new_amount = validated_data.get("total_amount")
        if mark_paid:
            TransactionHistory.objects.create(
                invoice=instance,
                metadata={"invoices": [instance.code]},
                merchant_membership=request.membership,
                is_online=False,
                credit=instance.due_amount,
                type=TransactionHistory.TYPES.BILLING,
                transaction_type=TransactionHistory.TRANSACTION_TYPE.CREDIT,
            )
            instance.status = Invoice.STATUS.PAID
            instance.due_amount = Decimal(0)
            instance.handled_by = request.membership.member
            instance.save()
            return instance
        if new_amount and not instance.total_amount == new_amount:
            metadata = validated_data.get("metadata", {})
            if self.instance.total_amount > new_amount:
                # if new amount is less then previous amount
                remaining_amount = self.instance.total_amount - new_amount
                TransactionHistory.objects.create(
                    invoice=instance,
                    metadata={"invoices": [instance.code], "invoice_info": metadata},
                    merchant_membership=request.membership,
                    is_online=False,
                    credit=remaining_amount,
                    type=TransactionHistory.TYPES.BILLING,
                    transaction_type=TransactionHistory.TRANSACTION_TYPE.ADJUSTMENT,
                )
                instance.due_amount = instance.due_amount - remaining_amount
            elif self.instance.total_amount < new_amount:
                # if new amount is greater then previous amount
                difference = new_amount - self.instance.total_amount
                TransactionHistory.objects.create(
                    invoice=instance,
                    metadata={"invoices": [instance.code], "invoice_info": metadata},
                    merchant_membership=request.membership,
                    is_online=False,
                    debit=difference,
                    type=TransactionHistory.TYPES.BILLING,
                    transaction_type=TransactionHistory.TRANSACTION_TYPE.DEBIT,
                )
                instance.due_amount = instance.due_amount + difference
            instance.total_amount = new_amount
            old_remarks = instance.metadata.get("remarks", "")
            new_remarks = metadata.get("remarks", "")
            new_remarks = f"{old_remarks}{new_remarks}. "
            instance.metadata["remarks"] = new_remarks
            instance.save()
            return instance
        return instance
