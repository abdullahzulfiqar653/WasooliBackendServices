from django.contrib import admin
from django.db.models import Count
from apis.models.merchant_member import MerchantMember


@admin.register(MerchantMember)
class MerchantMemberAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "code",
        "merchant",
        "primary_phone",
        "merchant_count",
        "user_first_name",
    )
    list_filter = ("roles__role",)
    search_fields = ("user__first_name", "user__last_name", "primary_phone", "code")
    ordering = ("-code",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            merchant_count=Count("merchant_memberships"),
        )
        return queryset.select_related("merchant", "user")

    def user_first_name(self, obj):
        return obj.user.first_name

    user_first_name.short_description = "First Name"

    def merchant_count(self, obj):
        return obj.merchant_count

    merchant_count.short_description = "Memberships Count"
