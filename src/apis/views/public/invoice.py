from rest_framework import generics

from apis.permissions import IsCustomer
from apis.serializers.invoice import InvoiceSerializer

from drf_spectacular.utils import extend_schema


class PublicMemberInvoiceListAPIView(generics.ListAPIView):
    pagination_class = None
    permission_classes = [IsCustomer]
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        return self.request.member.invoices.order_by("-created_at").all()

    @extend_schema(
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
