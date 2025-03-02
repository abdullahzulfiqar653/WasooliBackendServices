from django.contrib import admin
from django.db.models import Prefetch
from apis.models.merchant_membership import MerchantMembership


@admin.register(MerchantMembership)
class MerchantMembershipAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "is_active",
        "is_monthly",
        "member_name",
        "account_code",
        "role_display",
        "actual_price",
        "merchant_name",
        "discounted_price",
    )
    list_filter = ("is_active", "merchant", "member__roles__role")
    search_fields = (
        "account",
        "member__code",
        "merchant__name",
        "member__primary_phone",
        "member__user__first_name",
    )
    ordering = ("-account",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        roles_queryset = Prefetch("member__roles", queryset=self.model.objects.none())
        return queryset.select_related(
            "merchant",
            # "member",
            "member__user",
        ).prefetch_related(roles_queryset)

    list_per_page = 1000

    def member_name(self, obj):
        return f"{obj.member.user.first_name}"

    member_name.short_description = "Member Name"

    def account_code(self, obj):
        return f"{obj.account} - {obj.member.code}"

    account_code.short_description = "Acc and MemberCode"

    def merchant_name(self, obj):
        return obj.merchant.name

    merchant_name.admin_order_field = "merchant__name"
    merchant_name.short_description = "Merchant Name"

    def role_display(self, obj):
        roles = obj.member.roles.all()  # No additional query, since it's pre-fetched
        if roles.exists():
            return roles.first().role
        return "No Role"

    role_display.admin_order_field = "role"
    role_display.short_description = "Role"
