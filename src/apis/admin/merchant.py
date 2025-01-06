from django.contrib import admin
from apis.models.merchant import Merchant

# from .forms import CommissionStructureForm


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    # form = CommissionStructureForm  # Use the custom form

    # Optionally, you can customize the fields you want to display in the admin interface
    list_display = (
        "name",
        "cash_commission_rate",
        "online_commission_rate",
        "commission_structure",
    )
    search_fields = ("name",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.all()
