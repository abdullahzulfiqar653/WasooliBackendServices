from django.db import models

from apis.models.abstract.base import BaseModel


class TransactionHistory(BaseModel):
    class TYPES(models.TextChoices):
        DEBIT = "Debit", "Debit"
        CREDIT = "Credit", "Credit"
        Refund = "Refund", "Refund"

    merchant_membership = models.ForeignKey(
        "apis.MerchantMembership", on_delete=models.CASCADE, related_name="transactions"
    )
    balance = models.DecimalField(max_digits=7, decimal_places=2)
    credit = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    debit = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    type = models.CharField(max_length=20, choices=TYPES.choices)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"User Balance: {self.merchant_membership.total_balance}"

    class Meta:
        ordering = ["-created_at"]
