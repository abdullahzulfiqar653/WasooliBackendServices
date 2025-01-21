from django.db import models

from django.db.models import Max
from django.utils import timezone

from apis.models.abstract.base import BaseModel
from apis.models.transaction_history import TransactionHistory


class Invoice(BaseModel):
    class STATUS(models.TextChoices):
        PAID = "paid", "Paid"
        UNPAID = "unpaid", "Unpaid"

    status = models.CharField(
        max_length=15, choices=STATUS.choices, default=STATUS.UNPAID
    )
    is_monthly = models.BooleanField(default=True)
    metadata = models.JSONField(null=True, blank=True)
    is_user_invoice = models.BooleanField(default=True)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    due_amount = models.DecimalField(max_digits=8, decimal_places=2)
    due_date = models.DateField(default=timezone.now() + timezone.timedelta(days=15))
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

    def __str__(self):
        return f"Invoice for {self.member.user.first_name}"

    def save(self, *args, **kwargs):
        if not self.code:
            last_code = Invoice.objects.aggregate(Max("code"))["code__max"]
            self.code = str(int(last_code) + 1) if last_code else "10000000"
        if self._state.adding:
            self.due_amount = self.total_amount
        super().save(*args, **kwargs)

    def apply_payment(merchant_membership, payment_amount):
        # Get all unpaid invoices, ordered by created at date (oldest first)
        invoices = merchant_membership.invoices.filter(status="unpaid").order_by(
            "created_at"
        )
        remaining_payment = payment_amount
        paid_invoices = []
        for invoice in invoices:
            if remaining_payment >= invoice.amount_due:
                remaining_payment -= invoice.amount_due
                # Fully pay this invoice
                invoice.amount_due = 0
                invoice.status = Invoice.STATUS.PAID
                invoice.save()
                paid_invoices.append(invoice.code)
            else:
                invoice.amount_due -= remaining_payment
                invoice.status = Invoice.STATUS.UNPAID
                paid_invoices.append(invoice.code)
                invoice.save()
                break

        transaction = TransactionHistory.objects.create(
            merchant_membership=merchant_membership,
            transaction_type=TransactionHistory.TYPES.CREDIT,
            credit=payment_amount,
            description=f"Payment for Invoice {invoice.id}",
        )
        transaction.balance = merchant_membership.total_balance
        transaction.save()
