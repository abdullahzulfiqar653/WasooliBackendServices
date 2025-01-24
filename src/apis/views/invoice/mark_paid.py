from rest_framework import generics

from apis.permissions import IsMerchantOrStaff
from apis.serializers.invoice.mark_paid import InvoiceMarkPaidSerializer


class InvoiceMarkPaidAPIView(generics.CreateAPIView):
    """
    This view mark `Invoice` as `paid`.
    This view is only accessible by `Merchant` or `Staff`.
    No payload is required.
    """

    permission_classes = [IsMerchantOrStaff]
    serializer_class = InvoiceMarkPaidSerializer

    def get_queryset(self):
        return self.request.member.invoices.all()
