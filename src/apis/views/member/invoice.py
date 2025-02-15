from rest_framework import generics, filters

from apis.permissions import IsMerchantOrStaff
from apis.serializers.invoice import InvoiceSerializer

from drf_spectacular.utils import extend_schema


class MemberInvoiceListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsMerchantOrStaff]
    filter_backends = [filters.SearchFilter]

    def get_queryset(self):
        return self.request.member.invoices.all().order_by("-created_at")

    @extend_schema(
        description="""
### Create a new invoice:
- `mark_paid`: a flag that indicates paid or unpaid invoices.\n
- `member_id`(required): The ID of the member .\n
- `metadata`: A dictionary representing additional information with key:value pairs (e.g., {"order_id": "1234"}).\n
- `amount`: Total invoice amount (e.g., 1500).\n
- `due_date`: Due date for the invoice (e.g., "2025-01-21"). Default is today's date if not provided.

The request body should include all these fields. The response will return the newly created invoice with a unique `id`.
        """,
        request=InvoiceSerializer,
        responses={
            201: InvoiceSerializer,
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @extend_schema(
        description="""
### List all invoices for the member:

**Request Parameters**
- `member_id`: The ID of the member .\n
**Response**\n
This endpoint returns a list of all invoices associated with the member, including:
- `id`: The unique identifier for the invoice.\n
- `amount`: The total invoice amount.\n
- `due_date`: The due date of the invoice.\n
- `metadata`: The additional metadata associated with the invoice (if any).\n
- `created_at`: The timestamp when the invoice was created.\n

        """,
        responses={
            200: InvoiceSerializer(many=True),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
