from rest_framework import generics

from apis.permissions import IsMerchantOrStaff
from apis.serializers.invoice import InvoiceSerializer


class InvoiceRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """
    This view to retrive, update invoice of `Members`.
    """

    permission_classes = [IsMerchantOrStaff]
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        return self.request.membership.member.invoices.all()
