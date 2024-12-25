from django.db import models
from django.db.models import Max
from django.utils import timezone

from apis.models.abstract.base import BaseModel
from apis.models.transaction_history import TransactionHistory


class Invoice(BaseModel):
    class STATUS(models.TextChoices):
        UNPAID = "unpaid", "Unpaid"
        PAID = "paid", "Paid"

    class TYPES(models.TextChoices):
        MONTHLY = "monthly", "Monthly"
        PAID = "paid", "Paid"

    merchant_membership = models.ForeignKey(
        "apis.MerchantMembership", on_delete=models.CASCADE, related_name="invoices"
    )
    type = models.CharField(max_length=50, choices=TYPES.choices, default=TYPES.MONTHLY)
    status = models.CharField(
        max_length=20, choices=STATUS.choices, default=STATUS.UNPAID
    )
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField(default=timezone.now() + timezone.timedelta(days=15))
    description = models.TextField(null=True, blank=True)
    # New column to store the invoice code, starting from 10000000
    code = models.CharField(max_length=9, unique=True, editable=False)

    def __str__(self):
        return f"Invoice for {self.merchant_membership.member.user.first_name}"

    def save(self, *args, **kwargs):
        if not self.code:
            last_code = Invoice.objects.aggregate(Max("code"))["code__max"]
            self.code = str(int(last_code) + 1) if last_code else "10000000"
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
