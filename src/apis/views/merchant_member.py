from rest_framework import generics
from django.db.models import Subquery, OuterRef

from apis.models.merchant_member import MerchantMember
from apis.models.merchant_membership import MerchantMembership

from apis.permissions import IsMerchantOrStaff
from apis.serializers.merchant_member import MerchantMemberSerializer


class MerchantMemberListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsMerchantOrStaff]
    serializer_class = MerchantMemberSerializer

    def get_queryset(self):
        merchant = self.request.user.merchant
        # Ensure that MerchantMember has a related_name `memberships` to the MerchantMembership model
        memberships = MerchantMembership.objects.filter(
            merchant=merchant, member_id=OuterRef("pk")
        ).order_by(
            "-is_active"
        )  # Assuming there might be multiple memberships, prioritize active ones

        # Annotate each member with the active status of their membership with the current merchant
        queryset = MerchantMember.objects.filter(
            memberships__merchant=merchant
        ).annotate(
            current_active=Subquery(memberships.values("is_active")[:1]),
            area_name=Subquery(memberships.values("area")[:1]),
        )

        return queryset


class MerchantMemberRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsMerchantOrStaff]
    serializer_class = MerchantMemberSerializer

    def get_queryset(self):
        merchant = self.request.user.merchant
        # Ensure that MerchantMember has a related_name `memberships` to the MerchantMembership model
        memberships = MerchantMembership.objects.filter(
            merchant=merchant, member_id=OuterRef("pk")
        ).order_by(
            "-is_active"
        )  # Assuming there might be multiple memberships, prioritize active ones

        # Annotate each member with the active status of their membership with the current merchant
        queryset = MerchantMember.objects.filter(
            memberships__merchant=merchant
        ).annotate(
            current_active=Subquery(memberships.values("is_active")[:1]),
            area_name=Subquery(memberships.values("area")[:1]),
        )

        return queryset
