from rest_framework import generics
from rest_framework.response import Response

from apis.utils import get_customer_stats
from apis.permissions import IsMerchantOrStaff
from apis.serializers.member_profile import MemberProfileSerializer


class MemberProfileRetrieveAPIView(generics.RetrieveAPIView):
    """
    This endpoint provides all the information for members profile cards.
    """

    permission_classes = [IsMerchantOrStaff]
    serializer_class = MemberProfileSerializer

    def retrieve(self, request, *args, **kwargs):
        membership = request.membership
        response = get_customer_stats(membership)
        return Response(response)
