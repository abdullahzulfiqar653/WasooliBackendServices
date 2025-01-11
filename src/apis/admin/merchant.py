from django.contrib import admin
from apis.models.lookup import Lookup
from apis.models.merchant_member import MerchantMember
from apis.models.merchant_membership import MerchantMembership


from apis.models.merchant import Merchant

admin.site.register(Lookup)
admin.site.register(MerchantMember)
admin.site.register(MerchantMembership)


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):

    # Optionally, you can customize the fields you want to display in the admin interface
    list_display = (
        "name",
        "type",
        "code",
        "commission_structure",
    )
    search_fields = ("name",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.all()
