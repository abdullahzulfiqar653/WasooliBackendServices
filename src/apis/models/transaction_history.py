from decimal import Decimal

from django.db import models
from django.db.models import Sum

from apis.models.invoice import Invoice
from apis.models.abstract.base import BaseModel


class TransactionHistory(BaseModel):
    UID_PREFIX = 106

    class TYPES(models.TextChoices):
        COMMISSION = "commission", "Commission"
        BILLING = "billing", "Billing"

    class TRANSACTION_TYPE(models.TextChoices):
        DEBIT = "debit", "Debit"
        CREDIT = "credit", "Credit"
        REFUND = "refund", "Refund"
        ADJUSTMENT = "adjustment", "Adjustment"

    merchant_membership = models.ForeignKey(
        "apis.MerchantMembership",
        null=True,
        on_delete=models.SET_NULL,
        related_name="membership_transactions",
    )
    merchant = models.ForeignKey(
        "apis.Merchant",
        null=True,
        on_delete=models.SET_NULL,
        related_name="member_transactions",
    )
    invoice = models.ForeignKey(
        "apis.Invoice",
        null=True,
        on_delete=models.SET_NULL,
        related_name="member_invoices",
    )
    metadata = models.JSONField(null=True, blank=True)
    is_commission_paid = models.BooleanField(default=False)
    is_online = models.BooleanField(null=True, default=None)
    value = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    commission = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    type = models.CharField(max_length=20, choices=TYPES.choices, default=TYPES.BILLING)
    transaction_type = models.CharField(
        max_length=15, choices=TRANSACTION_TYPE.choices, default=TRANSACTION_TYPE.CREDIT
    )

    def __str__(self):
        return f"{self.id}"

    def adjust_credit_debit_balance(self):
        """
        Calculate the balance for this membership by summing all previous debits and credits.
        The balance is calculated by subtracting total debit from total credit.
        """
        # Calculate total debit and credit for this merchant_membership
        total_debit = (
            self.merchant_membership.membership_transactions.filter(
                transaction_type=self.TRANSACTION_TYPE.DEBIT
            ).aggregate(total_debit=Sum("value", default=0))["total_debit"]
            or 0
        )

        # Calculate total credit for this merchant_membership
        total_credit = (
            self.merchant_membership.membership_transactions.filter(
                transaction_type=self.TRANSACTION_TYPE.CREDIT
            ).aggregate(total_credit=Sum("value", default=0))["total_credit"]
            or 0
        )

        total_adjustment = (
            self.merchant_membership.membership_transactions.filter(
                transaction_type=self.TRANSACTION_TYPE.ADJUSTMENT
            ).aggregate(total_adjustmnet=Sum("value", default=0))["total_adjustmnet"]
            or 0
        )

        # Include the current transaction's debit or credit
        credit = debit = adjustment = 0
        if self.transaction_type == self.TRANSACTION_TYPE.CREDIT:
            credit = self.value
        if self.transaction_type == self.TRANSACTION_TYPE.DEBIT:
            debit = self.value
        if self.transaction_type == self.TRANSACTION_TYPE.ADJUSTMENT:
            adjustment = self.value

        total_debit += debit
        total_credit += credit
        total_adjustment += adjustment

        # Update the balance
        self.balance = total_credit - (total_debit - total_adjustment)

    def calculate_commission(self):
        """
        Calculate commission based on the merchant's commission structure.
        Commission can be either for cash or online transactions, determined by the `is_online` flag.
        """
        commission_rate = Decimal(0)
        if self.merchant:
            commission_rate = Decimal(
                self.get_commission_rate(self.merchant, self.is_online)
            )
        elif self.merchant_membership:
            # If the merchant is not available, fetch via merchant_membership
            merchant = self.merchant_membership.merchant
            commission_rate = Decimal(
                self.get_commission_rate(merchant, self.is_online)
            )

        return self.value * commission_rate / Decimal(100)

    def get_commission_rate(self, merchant, is_online):
        """
        Retrieve the commission rate based on the payment method and tiers.
        :param merchant: The merchant whose commission structure to use
        :param is_online: Boolean indicating whether the payment was online or not
        """
        commission_structure = merchant.commission_structure
        payment_type = "online" if is_online else "cash"
        tiers = commission_structure.get(payment_type, [])

        # Find the tier based on credit amount
        for tier in tiers:
            if self.value <= tier["max_credit"]:
                return tier["commission"]
        return 0

    def apply_payment(self):
        # Get all unpaid invoices, ordered by created at date (oldest first)

        merchant_membership = self.merchant_membership
        invoices = merchant_membership.member.invoices.filter(status="unpaid").order_by(
            "created_at"
        )
        remaining_payment = self.value
        paid_invoices = []
        previous_invoice_state = []
        # Save the previous state of the invoices
        for invoice in invoices:
            previous_invoice_state.append(
                {
                    "id": invoice.id,
                    "status": invoice.status,
                    "due_amount": str(invoice.due_amount),
                }
            )

        for invoice in invoices:
            if remaining_payment >= invoice.due_amount:
                remaining_payment -= invoice.due_amount
                invoice.due_amount = 0
                invoice.status = Invoice.STATUS.PAID
                invoice.handled_by=self._merchant_member
                invoice.metadata['mark_as_paid_by'] = self._created_by
                invoice.save()
                paid_invoices.append(
                    {
                        "code": invoice.code,
                        "status": invoice.status,
                        "due_amount": str(invoice.due_amount),
                        "total_amount": str(invoice.total_amount),
                        "created_at": invoice.created_at.isoformat(),
                        "updated_at": invoice.updated_at.isoformat(),
                        "metadata": invoice.metadata
                    }
                )
            else:
                invoice.due_amount -= remaining_payment
                invoice.status = Invoice.STATUS.UNPAID
                invoice.handled_by=self._merchant_member
                invoice.metadata = invoice.metadata or {}
                invoice.metadata['mark_as_paid_by'] = self._created_by
                invoice.save()
                paid_invoices.append(
                    {
                        "code": invoice.code,
                        "status": invoice.status,
                        "due_amount": str(invoice.due_amount),
                        "total_amount": str(invoice.total_amount),
                        "created_at": invoice.created_at.isoformat(),
                        "updated_at": invoice.updated_at.isoformat(),
                        "metadata": invoice.metadata
                    }
                )
                break
        self.metadata = {
            "created_by": self._created_by,
            "invoices": paid_invoices,
            "previous_invoice_state": previous_invoice_state,
        }
        self.save()

    def revert_transaction(self):
        # Retrieve the previous state from metadata
        previous_invoice_state = self.metadata.get("previous_invoice_state", [])

        # Prepare a list to hold the invoices that need to be updated
        invoices_to_update = []

        # Collect the invoices based on their ids
        invoice_ids = [invoice["id"] for invoice in previous_invoice_state]
        invoices = (
            Invoice.objects.filter(id__in=invoice_ids)
            .exclude(status=Invoice.STATUS.CANCELLED)
            .order_by("created_at")
        )

        # Iterate through the invoices and update the status and due_amount
        for invoice, invoice_data in zip(invoices, previous_invoice_state):
            invoice.status = invoice_data["status"]
            invoice.due_amount = invoice_data["due_amount"]
            invoices_to_update.append(invoice)

        # Perform a bulk update on the invoices
        if invoices_to_update:
            Invoice.objects.bulk_update(
                invoices_to_update, fields=["status", "due_amount"]
            )

        # Delete the current transaction object
        self.delete()  # This will delete the current transaction history record

    def save(self, *args, **kwargs):
        billing = self.type == self.TYPES.BILLING
        is_credit = self.transaction_type == self.TRANSACTION_TYPE.CREDIT
        # Only calculate commission if the type is Billing and it's a credit transaction
        if self._state.adding:
            if billing and is_credit:
                self.commission = self.calculate_commission()
            self.adjust_credit_debit_balance()
        super().save(*args, **kwargs)

    class Meta:
        get_latest_by = "created_at"
        indexes = [
            models.Index(
                fields=[
                    "type",
                    "created_at",
                    "transaction_type",
                    "merchant_membership",
                ]
            ),
            models.Index(
                fields=[
                    "type",
                    "transaction_type",
                    "is_commission_paid",
                    "merchant_membership",
                ]
            ),
            models.Index(fields=["-created_at"]),
            models.Index(fields=["merchant", "type", "transaction_type"]),
        ]
        ordering = ["-created_at"]
