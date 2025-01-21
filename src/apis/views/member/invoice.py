from rest_framework import generics, filters

from apis.permissions import IsMerchantOrStaff
from apis.serializers.invoice import InvoiceSerializer


class MemberInvoiceListCreateAPIView(generics.ListCreateAPIView):
    """
    This endpoint is used to list all invoices of a member and to create a new invoice.

    - **To create a new invoice**, the following parameters are required:
    - `metadata`: A string representing additional information.
    - `amount`: The total invoice amount (e.g., "1500").
    - `amount_due`: The amount due (e.g., "0 or 1000").
    - `due_date`: The due date for the invoice (e.g., "2025-01-21"). By default, the current date is used.

    - **To list invoices**, the response will include the following fields for each invoice:
    - `status`: The current status of the invoice.
    - `is_monthly`: A flag indicating if the invoice is monthly.
    - `metadata`: Additional information related to the invoice.
    - `amount`: The total amount of the invoice.
    - `amount_due`: The amount still due on the invoice.
    - `due_date`: The due date of the invoice.
    - `code`: A unique code identifying the invoice.
    - `handled_by`: The person or system handling the invoice.
    """

    serializer_class = InvoiceSerializer
    permission_classes = [IsMerchantOrStaff]
    filter_backends = [filters.SearchFilter]

    def get_queryset(self):
        return self.request.member.invoices.all()
