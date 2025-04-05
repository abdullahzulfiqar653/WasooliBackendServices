import secrets
from django.db.models import Max
from django.utils import timezone
from rest_framework import serializers
from django.db.models import OuterRef, Exists

from apis.models.invoice import Invoice
from apis.models.transaction_history import TransactionHistory


class MonthlyMembershipInvoiceSerializer(serializers.Serializer):

    def create(self, validated_data):
        request = self.context["request"]
        merchant = request.merchant
        now = timezone.now()
        current_year = now.year
        current_month = validated_data.get("month", now.month)

        # Subquery: Check if an invoice exists for the current month for a given membership
        unpaid_invoices = Invoice.objects.filter(
            type=Invoice.Type.MONTHLY,
            status=Invoice.STATUS.UNPAID,
            created_at__year=current_year,
            membership__merchant=merchant,
            created_at__month=current_month,
        )
        adjustments = []
        for invoice in unpaid_invoices:
            id = secrets.token_hex(6)
            adjustments.append(
                TransactionHistory(
                    invoice=invoice,
                    is_online=False,
                    value=invoice.total_amount,
                    type=TransactionHistory.TYPES.BILLING,
                    metadata={"invoices": [invoice.code]},
                    merchant_membership=invoice.membership,
                    id=f"{TransactionHistory.UID_PREFIX}{id}",
                    transaction_type=TransactionHistory.TRANSACTION_TYPE.ADJUSTMENT,
                )
            )
        TransactionHistory.objects.bulk_create(adjustments)
        unpaid_invoices.update(status=Invoice.STATUS.CANCELLED)

        invoice_exists_subquery = Invoice.objects.filter(
            membership=OuterRef("id"),
            created_at__year=current_year,
            created_at__month=current_month,
            status=Invoice.Type.MONTHLY,
        ).exclude(status=Invoice.STATUS.CANCELLED)
        memberships = merchant.members.annotate(
            has_invoice=Exists(invoice_exists_subquery)
        ).filter(has_invoice=False)

        invoices = []
        transactions = []
        invoice = (
            Invoice.objects.filter(membership__merchant=merchant)
            .order_by("-code")
            .first()
        )

        try:
            for membership in memberships:
                membership._supply_month = current_month
                last_code = (
                    str(int(invoice.code) + 1) if invoice else f"{merchant.code}100000"
                )
                merchant_member = membership.member
                amount_to_pay = membership.calculate_invoice()
                id = secrets.token_hex(6)
                invoice = Invoice(
                    metadata={},
                    code=last_code,
                    membership=membership,
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
