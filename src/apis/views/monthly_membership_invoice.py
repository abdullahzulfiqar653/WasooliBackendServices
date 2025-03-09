from rest_framework.generics import CreateAPIView
from apis.serializers.monthly_membership_invoice import (
    MonthlyMembershipInvoiceSerializer,
)


class MonthlyMembershipInvoiceCreateAPIView(CreateAPIView):
    serializer_class = MonthlyMembershipInvoiceSerializer
    permission_classes = []
