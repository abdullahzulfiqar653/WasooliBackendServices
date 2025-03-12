from datetime import datetime
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend

from apis.permissions import IsMerchantOrStaff
from apis.filters.invoice import InvoiceFilter
from apis.serializers.invoice import InvoiceSerializer
from apis.serializers.fake_invoice_serializer import FakeInvoiceSerializer

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter


class MemberInvoiceListCreateAPIView(generics.ListCreateAPIView):
    pagination_class = None
    filterset_class = InvoiceFilter
    serializer_class = InvoiceSerializer
    permission_classes = [IsMerchantOrStaff]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]

    def get_queryset(self):
        return self.request.membership.invoices.all().order_by("-created_at")

    @extend_schema(
        description="""
### Create a new invoice:
- `amount`: Total invoice amount (e.g., 1500).\n
- `metadata`: A dictionary representing additional information with key:value pairs (e.g., {"remarks": "payment for extra service"}).\n

The request body should include these fields. The response will return the newly created invoice with a unique `id`.
        """,
        request=FakeInvoiceSerializer,
        responses={
            201: InvoiceSerializer,
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="created_at_year",
                description="Year of creation for filtering invoice",
                required=False,
                type=OpenApiTypes.STR,
                enum=["2024", "2025", "2026", "2027", "2028", "2029", "2030"],
                default=str(datetime.now().year),
            ),
            OpenApiParameter(
                name="type",
                description="type of the invoice.",
                required=False,
                type=OpenApiTypes.STR,
                enum=["monthly", "miscellaneous"],
            ),
            OpenApiParameter(
                name="status",
                description="status of the invoice.",
                required=False,
                type=OpenApiTypes.STR,
                enum=["paid", "unpaid"],
            ),
        ],
        description="""
### List all invoices for the member:

**Response**\n
This endpoint returns a list of all invoices associated with the member, including following detail:
- `id`: The unique identifier for the invoice.\n
- `created_at`: The timestamp when the invoice was created.\n
- `status`: The current payment status of the invoice (e.g., paid, unpaid).\n
- `is_monthly`: A boolean value indicating whether the invoice is a recurring monthly invoice.\n
- `metadata`: The additional metadata associated with the invoice (if any).\n
- `total_amount`: The total invoice amount.\n
- `due_amount`: The remaining amount to be paid.
- `due_date`: The due date of the invoice.\n
- `code`: A unique reference code for the invoice.\n
- `type`: Specifies the type of invoice (e.g., monthly, one-time).\n
- `handled_by`: The unique identifier of the staff member handling the invoice.

        """,
        responses={
            200: InvoiceSerializer(many=True),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
