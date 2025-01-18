from django.contrib import admin
from apis.models.lookup import Lookup
from apis.models.member_role import MemberRole


from apis.models.merchant import Merchant

admin.site.register(Lookup)
admin.site.register(MemberRole)


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
    list_filter = ("type", "owner")
    search_fields = ("name", "owner__first_name", "code")

    def owner_first_name(self, obj):
        return obj.owner.first_name

    owner_first_name.admin_order_field = "owner__first_name"
    owner_first_name.short_description = "Owner First Name"

    def merchant_count(self, obj):
        return obj.members.count()

    merchant_count.short_description = "Number of Members"
