from django.db import models
from django.db.models import Sum
from django.utils import timezone
from apis.models.merchant import Merchant
from apis.models.abstract.base import BaseModel


class MerchantMembership(BaseModel):
    member = models.ForeignKey(
        "apis.MerchantMember",
        on_delete=models.CASCADE,
        related_name="member_memberships",
    )
    merchant = models.ForeignKey(
        "apis.Merchant", on_delete=models.CASCADE, related_name="merchant_memberships"
    )
    is_active = models.BooleanField(default=True)
    address = models.TextField(null=True)
    area = models.ForeignKey(
        "apis.Lookup",
        on_delete=models.SET_NULL,
        related_name="area_memberships",
        null=True,
    )
    city = models.ForeignKey(
        "apis.Lookup",
        on_delete=models.SET_NULL,
        related_name="city_memberships",
        null=True,
    )
    secondary_phone = models.CharField(max_length=10, null=True)
    picture = models.ImageField(upload_to="protected/picture", null=True)
    # Financial fields
    is_monthly = models.BooleanField(default=True)
    meta_data = models.JSONField(null=True, blank=True)
    account = models.CharField(max_length=6, unique=True, editable=False)
    actual_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ["member", "merchant"]

    def __str__(self):
        return f"{self.user.first_name} - {self.user.profile.role} of {self.merchant.name}."

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
        total = self.supply_records.filter(
            date__year=timezone.now().year, date__month=timezone.now().month
        ).aggregate(given=Sum("given"))
        return total["given"] or 0

    @property
    def total_supply_balance(self):
        total = self.supply_records.aggregate(given=Sum("given"), taken=Sum("taken"))
        return (total["given"] or 0) - (total["taken"] or 0)

    @property
    def total_credit(self):
        return (
            self.transactions.filter(type="credit").aggregate(Sum("credit"))[
                "credit__sum"
            ]
            or 0
        )

    @property
    def total_debit(self):
        total_debit = (
            self.transactions.filter(type="debit").aggregate(Sum("debit"))["debit__sum"]
            or 0
        )
        return total_debit

    @property
    def total_balance(self):
        return self.total_credit - self.total_debit

    def calculate_invoice(self):
        if self.merchant.type == Merchant.MerchantType.WATER and not self.is_monthly:
            return self.total_supply_given_this_month * self.discounted_price
        return self.discounted_price
