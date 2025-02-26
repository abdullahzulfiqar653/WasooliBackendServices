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
| `mark_paid`    | ✅ Yes     | If `mark_paid` is set to `true`, the invoice will be marked as `paid` and all other fields will be ignored,  |
| `total_amount` | ✅ Yes                 | To update the total_amount, `mark_paid` must be set to false. .if total_amount is sent then it requires meta data field to be sent as well|
| `metadata`(`dictionary`)     | ✅ Yes   | The metadata field is mandatory when updating the total_amount. It must include a `remarks` attribute explaining why the amount is being changed. |
| `settlement` | ✅ Yes | If `settlement` is set to `true`, the invoice will be marked as `settled`, and any remaining due amount will be cleared. |

""",
        responses={200: InvoiceSerializer()},
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
