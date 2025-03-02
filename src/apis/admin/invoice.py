from django.contrib import admin
from apis.models import Invoice


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "member",
        "status",
        "is_monthly",
        "handled_by",
        "created_at",
        "due_amount",
        "total_amount",
    )
    list_filter = (
        "status",
        "due_date",
        "created_at",
        "is_monthly",
        "is_user_invoice",
    )
    search_fields = (
        "code",
        "member__user__email",
        "member__primary_phone",
        "member__user__first_name",
    )
    ordering = ("-created_at",)
    readonly_fields = ("code", "created_at", "updated_at")
    fieldsets = (
        (
            "Invoice Details",
            {
                "fields": (
                    "code",
                    "status",
                    "is_monthly",
                    "is_user_invoice",
                    "total_amount",
                    "due_amount",
                    "due_date",
                    "metadata",
                )
            },
        ),
        (
            "Relations",
            {
                "fields": ("member", "handled_by"),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )
    actions = ["mark_as_paid"]

    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status=Invoice.STATUS.PAID)
        self.message_user(request, f"{updated} invoices marked as paid.")

    mark_as_paid.short_description = "Mark selected invoices as paid"
