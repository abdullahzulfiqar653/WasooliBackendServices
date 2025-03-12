from rest_framework.generics import CreateAPIView
from apis.serializers.monthly_membership_invoice import (
    MonthlyMembershipInvoiceSerializer,
)

from apis.permissions import IsMerchantOrStaff


class MerchantMonthlyMembershipInvoiceCreateAPIView(CreateAPIView):
    serializer_class = MonthlyMembershipInvoiceSerializer
    permission_classes = [IsMerchantOrStaff]
