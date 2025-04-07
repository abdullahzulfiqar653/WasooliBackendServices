from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from apis.permissions import IsCustomer
from apis.utils import get_customer_stats
from apis.models.merchant_membership import MerchantMembership
from apis.serializers.member_profile import MemberProfileSerializer

from drf_spectacular.utils import extend_schema


class PublicCustomerProfileRetrieveAPIView(generics.RetrieveAPIView):
    """
    This endpoint provides all the information for members profile cards.
    """

    permission_classes = [IsCustomer]
    serializer_class = MemberProfileSerializer

    def retrieve(self, request, *args, **kwargs):
        if not request.membership:
            raise NotFound({"detail": ["Customer Membership not found."]})

        response = get_customer_stats(request.membership)
        return Response(response)

    @extend_schema(
        description="""
### **Retrieve Customer Profile**

This API retrieves the profile details of a customer based on the provided **customer code** and **merchant ID**.

---

#### **Request Parameters**
| Parameter      | Required | Description |
|----------------|----------|-------------|
| `customer_code`| ✅ Yes   | The unique customer code identifying the customer. |
| `merchant ID`  | ✅ Yes   | The unique identifier for the each merchant. |

---
#### **Response Body**
The response contains a dictionary where each key represents a different card type.

- **total_spend**: Total amount spent by the customer.
- **total_remaining**: Remaining balance available.
- **total_saved**: Total amount saved by the customer.
- **supply_balance**: The supply balance.

Each of these fields contains a dictionary with following key, value pairs:
- **value**: integer value for that card.
- **name**:  Name to Display for that card.
""",
        responses={200: MemberProfileSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
