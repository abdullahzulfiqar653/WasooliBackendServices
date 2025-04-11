from django.db import models
from django.db.models import Sum
from django.utils import timezone
from apis.models.merchant import Merchant
from apis.models.abstract.base import BaseModel
from apis.models.transaction_history import TransactionHistory


class MerchantMembership(BaseModel):
    member = models.ForeignKey(
        "apis.MerchantMember",
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    merchant = models.ForeignKey(
        "apis.Merchant", on_delete=models.CASCADE, related_name="members"
    )
    address = models.TextField(null=True)
    area = models.CharField(max_length=128)
    city = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    picture = models.CharField(max_length=256, blank=True, null=True)
    secondary_phone = models.CharField(max_length=10, null=True, blank=True)
    # Financial fields
    is_monthly = models.BooleanField(default=True)
    meta_data = models.JSONField(null=True, blank=True)
    actual_price = models.DecimalField(max_digits=10, decimal_places=2)
    account = models.CharField(max_length=6, unique=True, editable=False)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_saved = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ["member", "merchant"]
        indexes = [
            models.Index(fields=["account"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["is_monthly"]),
            models.Index(fields=["-created_at"]),
            models.Index(fields=["member", "merchant", "is_active"]),
        ]

    def __str__(self):
        return f"{self.member.user.first_name} of {self.merchant.name}."

    def save(self, *args, **kwargs):
        if not self.account:
            last_account = MerchantMembership.objects.aggregate(models.Max("account"))[
                "account__max"
            ]
            self.account = str(int(last_account) + 1) if last_account else "10000"
        super().save(*args, **kwargs)

    @property
    def total_supply_given(self):
        total = self.supply_records.aggregate(given=Sum("given"))
        return total["given"] or 0

    @property
    def total_supply_given_this_month(self):
        now = timezone.now()
        month = getattr(self, "_supply_month", now.month)
        year = getattr(self, "_supply_year", now.year)
        total = self.supply_records.filter(
            created_at__year=year, created_at__month=month
        ).aggregate(given=Sum("given"))
        return total["given"] or 0

    @property
    def total_supply_balance(self):
        total = self.supply_records.aggregate(given=Sum("given"), taken=Sum("taken"))
        return (total["given"] or 0) - (total["taken"] or 0)

    @property
    def total_credit(self):
        return (
            self.transactions.filter(
                type=TransactionHistory.TRANSACTION_TYPE.CREDIT
            ).aggregate(Sum("value"))["value__sum"]
            or 0
        )

    @property
    def total_debit(self):
        total_debit = (
            self.transactions.filter(
                type=TransactionHistory.TRANSACTION_TYPE.DEBIT
            ).aggregate(Sum("value"))["value__sum"]
            or 0
        )
        return total_debit

    @property
    def total_balance(self):
        return self.total_credit - self.total_debit

    def calculate_invoice(self):
        if self.merchant.is_fixed_fee_merchant or self.is_monthly:
            return self.discounted_price
        return self.total_supply_given_this_month * self.discounted_price
