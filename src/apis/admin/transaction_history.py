from django.contrib import admin
from apis.models import TransactionHistory


@admin.register(TransactionHistory)
class TransactionHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "debit",
        "credit",
        "balance",
        "commission",
        "created_at",
        "transaction_type",
        "merchant_membership",
    )
    list_filter = (
        "type",
        "is_online",
        "created_at",
        "transaction_type",
    )
    search_fields = (
        "merchant_membership__merchant__name",
        "invoice__code",
        "metadata",
    )
    ordering = ("-created_at",)
    readonly_fields = ("balance", "commission", "created_at", "updated_at")
    fieldsets = (
        (
            "Transaction Details",
            {
                "fields": (
                    "merchant_membership",
                    "merchant",
                    "invoice",
                    "type",
                    "transaction_type",
                    "debit",
                    "credit",
                    "balance",
                    "commission",
                    "metadata",
                )
            },
        ),
        (
            "Flags",
            {
                "fields": ("is_commission_paid", "is_online"),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )
    actions = ["mark_commission_as_paid"]

    def mark_commission_as_paid(self, request, queryset):
        updated = queryset.update(is_commission_paid=True)
        self.message_user(request, f"{updated} transactions marked as commission paid.")

    mark_commission_as_paid.short_description = (
        "Mark selected transactions as commission paid"
    )
