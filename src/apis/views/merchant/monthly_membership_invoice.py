from rest_framework.generics import CreateAPIView
from apis.serializers.monthly_membership_invoice import (
    MonthlyMembershipInvoiceSerializer,
)

from apis.permissions import IsMerchantOrStaff


class MerchantMonthlyMembershipInvoiceCreateAPIView(CreateAPIView):
    """
    Just provide the merchant id in URL and for all customers of the merchant monthly invoices will be created
    """

    serializer_class = MonthlyMembershipInvoiceSerializer
    permission_classes = [IsMerchantOrStaff]
