from django.contrib import admin
from apis.models.supply_record import SupplyRecord


@admin.register(SupplyRecord)
class SupplyRecordAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "merchant_membership_account",
        "member_name",
        "given",
        "taken",
        "created_at",
    )
    search_fields = ("merchant_membership__account",)

    def merchant_membership_account(self, obj):
        return obj.merchant_membership.account

    merchant_membership_account.short_description = "Membership Code"

    def member_name(self, obj):
        return obj.merchant_membership.member.user.get_full_name()
    member_name.short_description = "Member Name"
