from datetime import datetime
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend

from apis.permissions import IsCustomer
from apis.filters.invoice import InvoiceFilter
from apis.serializers.invoice import InvoiceSerializer

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter


class PublicMemberInvoiceListAPIView(generics.ListAPIView):
    pagination_class = None
    permission_classes = [IsCustomer]
    serializer_class = InvoiceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = InvoiceFilter

    def get_queryset(self):
        return self.request.member.invoices.order_by("-created_at").all()

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
### **Retrieve Member Invoices**

This API retrieves all invoices associated with a member based on their customer code. 
It returns a list of invoices sorted by the creation date.

---

#### **Request Body**
The `customer code` is required as a query parameter to retrieve the invoices for the member.

---

#### **Response Body**
The response will contain a list of invoices for the member, ordered by the `created_at` timestamp. Each invoice will have the following fields:

| Field          | Description                        |
|----------------|------------------------------------|
| `id`           | The unique identifier for the invoice. |
| `created_at`   | The timestamp when the invoice was created. |
| `status`       | The status of the invoice (e.g., `paid`, `pending`). |
| `is_monthly`   | Whether the invoice is a monthly invoice (`true` or `false`). |
| `metadata`     | Additional metadata or notes about the invoice. |
| `total_amount` | The total amount of the invoice.   |
| `due_amount`   | The amount due for the invoice (can be `"-"` if no due amount). |
| `due_date`     | The due date for the invoice.      |
| `code`         | The customer code associated with the invoice. |
| `type`         | The type of invoice (e.g., `monthly`). |
| `handled_by`   | The person or system handling the invoice. |
```
""",
        responses={200: InvoiceSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
