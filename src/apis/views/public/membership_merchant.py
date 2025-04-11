from rest_framework import generics

from apis.permissions import IsCustomer
from apis.models.merchant import Merchant
from apis.models.merchant_membership import MerchantMembership
from apis.serializers.membership_merchant import MembershipMerchantSerializer

from drf_spectacular.utils import extend_schema


class PublicMembershipMerchantsListAPIView(generics.ListAPIView):
    pagination_class = None
    permission_classes = [IsCustomer]
    serializer_class = MembershipMerchantSerializer

    def get_queryset(self):
        member = self.request.member
        merchant_ids = MerchantMembership.objects.filter(member=member).values_list(
            "merchant", flat=True
        )
        return Merchant.objects.filter(id__in=merchant_ids)

    @extend_schema(
        description="""
### **Retrieve Membership Merchants**

This API retrieves all the merchants associated with a member based on their **customer code**.
The response provides details about each merchant that the member is linked with.

---

#### **Request Parameters**
| Parameter       | Required | Description |
|-----------------|----------|-------------|
| `customer_code` |  ✅ Yes  | The unique customer code used to fetch associated merchants. |

---

#### **Response Body**
The response will contain a list of merchants that the member is associated with.

| Field         | Description                        |
|---------------|----------------------------------- |
| `id`          | The unique identifier for the merchant. |
| `name`        | The name of the merchant. |

        """,
        responses={200: MembershipMerchantSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
