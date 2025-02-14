from rest_framework import generics, filters

from apis.permissions import IsMerchantOrStaff
from apis.serializers.invoice import InvoiceSerializer


class MemberInvoiceListCreateAPIView(generics.ListCreateAPIView):
    """
    This endpoint is used to list all invoices of a member and to create a new invoice.

    - **To create a new invoice**, the following parameters are required:
    - `metadata`: A dict representing additional information with key:value pairs.
    - `amount`: The total invoice amount (e.g., "1500").
    - `due_date`: The due date for the invoice (e.g., "2025-01-21"). By default, the current date is used.

    - **To list invoices**, the response will include the following fields for each invoice:
    """

    serializer_class = InvoiceSerializer
    permission_classes = [IsMerchantOrStaff]
    filter_backends = [filters.SearchFilter]

    def get_queryset(self):
        return self.request.member.invoices.all().order_by("-created_at")
