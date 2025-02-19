from rest_framework import generics
from rest_framework.response import Response

from apis.utils import get_customer_stats
from apis.permissions import IsMerchantOrStaff
from apis.serializers.member_profile import MemberProfileSerializer

from drf_spectacular.utils import extend_schema


class MemberProfileRetrieveAPIView(generics.RetrieveAPIView):
    """
This endpoint provides all the information for members profile cards.

**The response will include the following fields:**
- total_spend: Total amount spent by the member.
- total_remaining: Total remaining balance of the member.
- total_saved: Total amount saved by the member.
    """

    permission_classes = [IsMerchantOrStaff]
    serializer_class = MemberProfileSerializer

    def retrieve(self, request, *args, **kwargs):
        membership = request.membership
        response = get_customer_stats(membership)
        return Response(response)

    @extend_schema(
        description="""
### Updates a member's financial profile information:

This endpoint allows updating the financial details of a member.

**Request Body:**
- `total_spend`: Total amount spent by the member.\n
- `total_remaining`: Total remaining balance of the member.\n
- `total_saved`: Total amount saved by the member.

**Response:** Returns the updated financial details of the member
""",
        responses={
            200: MemberProfileSerializer,
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
