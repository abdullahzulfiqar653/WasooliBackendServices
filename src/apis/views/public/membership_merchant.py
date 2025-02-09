from rest_framework import generics

from apis.permissions import IsCustomer
from apis.models.merchant import Merchant
from apis.models.merchant_membership import MerchantMembership
from apis.serializers.membership_merchant import MembershipMerchantSerializer


class MembershipMerchantsListAPIView(generics.ListAPIView):
    """
    This endpoint retrieves all the merchants for a member based on their customer code.
    """

    def get_queryset(self):
        member = self.request.member

        merchant_ids = MerchantMembership.objects.filter(member=member).values_list(
            "merchant", flat=True
        )fhnfxhbrxthb
        return Merchant.objects.filter(id__in=merchant_ids)
    

        def get_queryset(self):
        member = self.request.member

        merchant_ids = MerchantMembership.objects.filter(member=member).values_list(
            "merchant", flat=True
        )
        return Merchant.objects.filter(id__in=merchant_ids)
