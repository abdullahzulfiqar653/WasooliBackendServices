from django.contrib import admin
from django.db.models import Count
from apis.models.lookup import Lookup

from apis.models.merchant import Merchant

admin.site.register(Lookup)


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "type",
        "code",
        "merchant_count",
        "owner_first_name",
    )
    ordering = ("name",)
    list_filter = ("type",)
    search_fields = ("name", "owner__first_name", "code")

    def get_queryset(self, request):
        # Annotate the queryset to include the count of related members
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(member_count=Count("members"))
        return queryset

    def owner_first_name(self, obj):
        return obj.owner.first_name

    owner_first_name.admin_order_field = "owner__first_name"
    owner_first_name.short_description = "Owner First Name"

    def merchant_count(self, obj):
        return obj.member_count

    merchant_count.short_description = "Number of Members"
