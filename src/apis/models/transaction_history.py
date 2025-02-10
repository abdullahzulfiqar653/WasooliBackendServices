from decimal import Decimal
from django.db import models
from django.db.models import Sum
from apis.models.abstract.base import BaseModel


class TransactionHistory(BaseModel):
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
    debit = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=9, decimal_places=2, default=0)
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
        totals = self.merchant_membership.membership_transactions.aggregate(
            total_debit=Sum("debit", default=0), total_credit=Sum("credit", default=0)
        )

        total_debit = totals.get("total_debit", 0)
        total_credit = totals.get("total_credit", 0)
        # Include the current transaction's debit or credit
        total_debit += self.debit or 0
        total_credit += self.credit or 0

        # Update the balance
        self.balance = total_credit - total_debit

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

        return self.credit * commission_rate / Decimal(100)

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
            if self.credit <= tier["max_credit"]:
                return tier["commission"]
        return 0

    def save(self, *args, **kwargs):
        # Only calculate commission if the type is Billing and it's a credit transaction
        if self.type == self.TYPES.BILLING and self.credit > 0:
            self.commission = self.calculate_commission()
        self.adjust_credit_debit_balance()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-invoice"]),
        ]
