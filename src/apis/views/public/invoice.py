from rest_framework import generics

from apis.permissions import IsCustomer
from apis.serializers.invoice import InvoiceSerializer


class PublicMemberInvoiceListAPIView(generics.ListAPIView):
    """
    This endpoint retrieves all the merchants for a member based on their customer code.
    """

    pagination_class = None
    permission_classes = [IsCustomer]
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        return self.request.member.invoices.order_by("-created_at").all()
