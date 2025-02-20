from rest_framework import generics
from rest_framework.response import Response

from apis.utils import get_customer_stats
from apis.permissions import IsMerchantOrStaff
from apis.serializers.member_profile import MemberProfileSerializer


class MemberProfileRetrieveAPIView(generics.RetrieveAPIView):
    """
    This endpoint provides all the information for members profile cards.

    **The response will include the following fields:**
    - total_spend: Total amount spent by the member.
    - total_remaining: Total remaining balance of the member.
    - total_saved: Total amount saved by the member.
    - supply_balance: if customer have any supply balance
    """

    permission_classes = [IsMerchantOrStaff]
    serializer_class = MemberProfileSerializer

    def retrieve(self, request, *args, **kwargs):
        membership = request.membership
        response = get_customer_stats(membership)
        return Response(response)
