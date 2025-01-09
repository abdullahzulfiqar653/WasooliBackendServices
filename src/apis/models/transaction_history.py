from django.db import models

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

    def calculate_commission(self):
        """
        Calculate commission based on the merchant's commission structure.
        Commission can be either for cash or online transactions, determined by the `is_online` flag.
        """
        commission_rate = 0
        if self.merchant:
            commission_rate = self.get_commission_rate(self.merchant, self.is_online)
        elif self.merchant_membership:
            # If the merchant is not available, fetch via merchant_membership
            merchant = self.merchant_membership.merchant
            commission_rate = self.get_commission_rate(merchant, self.is_online)

        return self.credit * commission_rate / 100

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

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]
