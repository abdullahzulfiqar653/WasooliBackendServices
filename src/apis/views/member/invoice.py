from rest_framework import generics, filters

from apis.permissions import IsMerchantOrStaff
from apis.serializers.invoice import InvoiceSerializer


class MemberInvoiceListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsMerchantOrStaff]
    filter_backends = [filters.SearchFilter]

    def get_queryset(self):
        return self.request.member.invoices.all()
