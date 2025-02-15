from rest_framework import generics

from apis.permissions import IsMerchantOrStaff
from apis.serializers.invoice import InvoiceSerializer

from drf_spectacular.utils import extend_schema


class InvoiceRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsMerchantOrStaff]
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        return self.request.membership.member.invoices.all().order_by("-created_at")

    @extend_schema(
        description="""
### **Handles Invoice Retrieval**

This API allows merchants or staff to retrieve  invoice details for `Members`.

---

#### **🟢 Request Parameters (Path)**
| Parameter |Required | Description |
|-----------|---------|-------------|
| `id`      | ✅ Yes | The ID of the invoice to retrieve or update. |

---
""",
        responses={200: InvoiceSerializer()},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        description="""
### **Handles Invoice Update**

This API allows merchants or staff to update invoice details for `Members`.

---

#### **📝 Request Body **
| Field          | Required   | Description |
|----------------|------------|-------------|
| `id`           | ✅ Yes    | The ID of the invoice to retrieve or update. |
| `mark_paid`    | ✅ Yes    | Flag indicating whether the invoice has been paid (`true` or `false`). |
| `metadata`     | ✅ Yes    | Additional metadata or notes about the invoice. |
| `total_amount` | ✅ Yes    | The updated total amount of the invoice. |
| `due_date`     | ✅ Yes    | The due date of the invoice. |
| `type`         | ✅ Yes    | The type of invoice (e.g., `monthly`). |

---
""",
        responses={200: InvoiceSerializer()},
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
