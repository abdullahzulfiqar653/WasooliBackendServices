from django.db import models
from django.db.models import Max
from django.utils import timezone

from apis.models.abstract.base import BaseModel


class Invoice(BaseModel):
    UID_PREFIX = 101

    class STATUS(models.TextChoices):
        PAID = "paid", "Paid"
        UNPAID = "unpaid", "Unpaid"
        CANCELLED = "cancel", "Cancel"

    class Type(models.TextChoices):
        OTHER = "other", "Other"
        MONTHLY = "monthly", "Monthly"
        ONE_TIME = "one_time", "One Time"
        MISCILLANEOUS = "miscellaneous", "Miscellaneous"

    status = models.CharField(
        max_length=15, choices=STATUS.choices, default=STATUS.UNPAID
    )
    is_monthly = models.BooleanField(default=True)
    metadata = models.JSONField(null=True, blank=True)
    is_user_invoice = models.BooleanField(default=True)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    due_amount = models.DecimalField(max_digits=8, decimal_places=2)
    due_date = models.DateField(
        default=(timezone.now() + timezone.timedelta(days=15)).date()
    )

    # New column to store the invoice code, starting from 10000000
    code = models.CharField(max_length=14, unique=True, editable=False)
    handled_by = models.ForeignKey(
        "apis.MerchantMember",
        null=True,
        on_delete=models.SET_NULL,
        related_name="handled_invoices",
    )
    member = models.ForeignKey(
        "apis.MerchantMember",
        null=True,
        on_delete=models.SET_NULL,
        related_name="invoices",
    )
    membership = models.ForeignKey(
        "apis.MerchantMembership",
        null=True,
        on_delete=models.SET_NULL,
        related_name="invoices",
    )
    type = models.CharField(max_length=15, choices=Type.choices, default=Type.MONTHLY)

    def __str__(self):
        return f"Invoice for {self.member.user.first_name}"

    def save(self, *args, **kwargs):
        if not self.code:
            invoice = (
                Invoice.objects.filter(membership__merchant=self.membership.merchant)
                .order_by("-code")
                .first()
            )
            self.code = (
                str(int(invoice.code) + 1)
                if invoice
                else f"{self.membership.merchant.code}100000"
            )
        if self._state.adding:
            if not (self.status == "paid" or self.due_amount):
                self.due_amount = self.total_amount
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["member", "type"]),
            models.Index(fields=["member", "status"]),
            models.Index(fields=["member", "created_at"]),
        ]
        ordering = ["-created_at"]
