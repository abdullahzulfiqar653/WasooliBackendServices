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
| `mark_paid`    | ✅ Yes (conditionally) | If only `mark_paid` is sent, it will be set to `true`. |
| `metadata`     | ✅ Yes (if `total_amount` is sent) | Required  if `total_amount` is also provided. |
| `total_amount` | ✅ Yes (if `metadata` is sent) | Required only if `metadata` is also provided. |

#### **📌 Notes**
- If only `mark_paid` is provided, the invoice will be marked as **paid** without updating `metadata` or `total_amount`.
- If `total_amount` is provided, then `metadata` is **also required**.
""",
        responses={200: InvoiceSerializer()},
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
