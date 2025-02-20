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
        merchant_id = self.kwargs.get("merchant_id")

        # Now fetch the MerchantMembership
        membership = MerchantMembership.objects.filter(
            member=request.member, merchant__id=merchant_id
        ).first()

        if not membership:
            raise NotFound({"detail": ["Customer Membership not found."]})

        response = get_customer_stats(membership)
        return Response(response)

    @extend_schema(
        description="""
### **Retrieve Customer Profile**

This API retrieves the profile details of a customer based on the provided **customer code** and **merchant ID**.

---

#### **Request Parameters**
| Parameter     | Required | Description |
|---------------|----------|-------------|
| `customer_code`| ✅ Yes | The unique customer code identifying the customer. |

---

#### **Response Body**
The response contains the full profile details of the customer including :-
- `total spend `

- `remaining balance`

- `savings`
""",
        responses={200: MemberProfileSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
