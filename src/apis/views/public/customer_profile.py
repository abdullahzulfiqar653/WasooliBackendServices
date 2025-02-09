from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from apis.utils import get_customer_stats
from apis.models.member_role import RoleChoices
from apis.models.merchant_member import MerchantMember
from apis.models.merchant_membership import MerchantMembership
from apis.serializers.member_profile import MemberProfileSerializer


class PublicCustomerProfileRetrieveAPIView(generics.RetrieveAPIView):
    """
    This endpoint provides all the information for members profile cards.
    """

    permission_classes = []
    serializer_class = MemberProfileSerializer

    def retrieve(self, request, *args, **kwargs):
        customer_code = self.kwargs.get("customer_code")
        merchant_id = self.kwargs.get("merchant_id")
        # Fetch the MerchantMember based on the provided customer code
        member = MerchantMember.objects.filter(code=customer_code).first()

        if not member:
            raise NotFound(detail="Customer with the provided code not found.")

        # Ensure that the member has the 'Customer' role for this merchant
        is_customer = member.roles.filter(role=RoleChoices.CUSTOMER).exists()

        if not is_customer:
            raise NotFound(detail="You do not own any service.")

        # Now fetch the MerchantMembership
        membership = MerchantMembership.objects.filter(
            member=member, merchant__id=merchant_id
        ).first()

        if not membership:
            raise NotFound(detail="Customer membership not found.")

        response = get_customer_stats(membership)
        return Response(response)
