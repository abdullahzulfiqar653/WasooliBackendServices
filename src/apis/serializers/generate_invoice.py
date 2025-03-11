import uuid
from uuid import uuid4

from django.utils import timezone
from rest_framework import serializers

from apis.models.invoice import Invoice
from apis.models.transaction_history import TransactionHistory
from apis.models.merchant_membership import MerchantMembership


class GenerateInvoicesSerializer(serializers.Serializer):
    def create(self, validated_data):
        request = self.context["request"]
        merchant = request.merchant
        memberships = merchant.members.all()

        invoices = []
        transactions = []

        invoices_created = False

        for membership in memberships:
            merchant_member = membership.member

            existing_invoice = Invoice.objects.filter(
                member=merchant_member,
                created_at__year=timezone.now().year,
                created_at__month=timezone.now().month,
            ).exists()

            if existing_invoice:
                continue

            invoices_created = True

            if merchant.is_fixed_fee_merchant:
                amount = membership.calculate_invoice()
            else:
                total_supply = membership.total_supply_given_this_month
                if total_supply:
                    amount = membership.calculate_invoice()
                elif membership.is_monthly:
                    amount = membership.calculate_invoice()
                else:
                    continue

            invoice = Invoice(
                member=merchant_member,
                status=Invoice.STATUS.UNPAID,
                total_amount=amount,
                due_amount=amount,
                code=str(uuid.uuid4()),
                created_at=timezone.now(),
            )
            invoice.id = str(uuid4())
            invoices.append(invoice)

        created_invoices = Invoice.objects.bulk_create(invoices)

        for invoice in created_invoices:
            merchant_membership = MerchantMembership.objects.filter(
                merchant=merchant, member=invoice.member
            ).first()

            transaction = TransactionHistory(
                invoice=invoice,
                transaction_type=TransactionHistory.TRANSACTION_TYPE.DEBIT,
                value=invoice.total_amount,
                is_online=False,
                merchant_membership=merchant_membership,
                metadata={
                    "invoice_code": invoice.code,
                    "created_at": str(timezone.now()),
                },
            )
            transaction.id = str(uuid4())
            transactions.append(transaction)

        TransactionHistory.objects.bulk_create(transactions)

        if invoices_created:
            return {"status": "success", "message": "Invoices generated successfully"}
        else:
            return {
                "status": "exists",
                "message": "Invoices already exist for this month",
            }
