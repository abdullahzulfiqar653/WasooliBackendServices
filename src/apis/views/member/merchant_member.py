from rest_framework import generics
from django.db.models import Subquery, OuterRef

from apis.models.member_role import RoleChoices
from apis.models.merchant_member import MerchantMember
from apis.models.merchant_membership import MerchantMembership

from apis.permissions import IsMerchantOrStaff
from apis.serializers.merchant_member import MerchantMemberSerializer


class MemberRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsMerchantOrStaff]
    serializer_class = MerchantMemberSerializer

    def get_queryset(self):
        role = self.request.query_params.get("role", RoleChoices.CUSTOMER).lower()
        role = RoleChoices.STAFF if role == "staff" else RoleChoices.CUSTOMER
        merchant = self.request.user.merchant
        # Ensure that MerchantMember has a related_name `memberships` to the MerchantMembership model
        memberships = MerchantMembership.objects.filter(
            merchant=merchant, member_id=OuterRef("pk")
        ).order_by(
            "-is_active"
        )  # Assuming there might be multiple memberships, prioritize active ones

        queryset = MerchantMember.objects.filter(
            roles__role__in=[
                RoleChoices.STAFF,
                RoleChoices.CUSTOMER,
                RoleChoices.MERCHANT,
            ]
        )

        # Conditionally add the filter based on the role
        if role == RoleChoices.STAFF:
            queryset = queryset.filter(
                merchant=merchant
            )  # For STAFF, use `merchant=merchant`
        else:
            queryset = queryset.filter(
                memberships__merchant=merchant
            )  # For CUSTOMER, use `memberships__merchant=merchant`

        # Annotate each member with the active status of their membership with the current merchant
        queryset = queryset.annotate(
            current_active=Subquery(memberships.values("is_active")[:1]),
            area_name=Subquery(memberships.values("area")[:1]),
        )

        return queryset
