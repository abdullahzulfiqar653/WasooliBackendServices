import secrets
from django.db.models import Max
from django.utils import timezone
from rest_framework import serializers

from apis.models.invoice import Invoice
from apis.models.transaction_history import TransactionHistory


class MonthlyMembershipInvoiceSerializer(serializers.Serializer):

    def create(self, validated_data):
        request = self.context["request"]
        merchant = request.merchant
        memberships = merchant.members.all()

        invoices = transactions = []

        last_code = Invoice.objects.aggregate(Max("code"))["code__max"]
        try:
            for membership in memberships:
                last_code = str(int(last_code) + 1) if last_code else "10000000"
                merchant_member = membership.member

                existing_invoice = Invoice.objects.filter(
                    membership=membership,
                    created_at__year=timezone.now().year,
                    created_at__month=timezone.now().month,
                ).exists()

                if existing_invoice:
                    continue

                amount_to_pay = membership.calculate_invoice()
                id = secrets.token_hex(6)
                invoice = Invoice(
                    code=last_code,
                    member=merchant_member,
                    due_amount=amount_to_pay,
                    created_at=timezone.now(),
                    total_amount=amount_to_pay,
                    status=Invoice.STATUS.UNPAID,
                    id=f"{Invoice.UID_PREFIX}{id}",
                )
                invoices.append(invoice)

                transactions.append(
                    TransactionHistory(
                        invoice=invoice,
                        value=invoice.total_amount,
                        merchant_membership=membership,
                        type=TransactionHistory.TYPES.BILLING,
                        id=f"{TransactionHistory.UID_PREFIX}{id}",
                        transaction_type=TransactionHistory.TRANSACTION_TYPE.DEBIT,
                    )
                )

            Invoice.objects.bulk_create(invoices)
            TransactionHistory.objects.bulk_create(transactions)
            return {}
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": "Please try again", "error": str(e)}
            )
