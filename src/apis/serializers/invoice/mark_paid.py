from decimal import Decimal
from rest_framework import serializers
from apis.models.invoice import Invoice
from apis.models.transaction_history import TransactionHistory


class InvoiceMarkPaidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        exclude = ["is_user_invoice", "member", "updated_at"]
        read_only_fields = [
            "status",
            "metadata",
            "total_amount",
            "due_amount",
            "handled_by",
            "code",
            "created_at",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        invoice = request.invoice
        if invoice.status != Invoice.STATUS.PAID:
            merchant_membership = request.merchant.members.filter(
                member=request.member
            ).first()
            TransactionHistory.objects.create(
                invoice=invoice,
                metadata={"invoices": [invoice.code]},
                merchant_membership=merchant_membership,
                is_online=False,
                credit=invoice.due_amount,
                type=TransactionHistory.TYPES.BILLING,
                transaction_type=TransactionHistory.TRANSACTION_TYPE.CREDIT,
            )
            invoice.status = Invoice.STATUS.PAID
            invoice.due_amount = Decimal(0)
            invoice.handled_by = request.member
            invoice.save()
        return invoice
