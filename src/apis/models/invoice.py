from django.db import models
from django.db.models import Max
from django.utils import timezone

from apis.models.abstract.base import BaseModel


class Invoice(BaseModel):
    class STATUS(models.TextChoices):
        CANCELLED = "cancel", "Cancel"
        PAID = "paid", "Paid"
        UNPAID = "unpaid", "Unpaid"

    class Type(models.TextChoices):
        MONTHLY = "monthly", "Monthly"
        ONE_TIME = "one_time", "One Time"
        OTHER = "other", "Other"
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
    code = models.CharField(max_length=10, unique=True, editable=False)
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
    type = models.CharField(max_length=15, choices=Type.choices, default=Type.MONTHLY)

    def __str__(self):
        return f"Invoice for {self.member.user.first_name}"

    def save(self, *args, **kwargs):
        if not self.code:
            last_code = Invoice.objects.aggregate(Max("code"))["code__max"]
            self.code = str(int(last_code) + 1) if last_code else "10000000"
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
