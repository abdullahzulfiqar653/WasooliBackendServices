from rest_framework import generics, filters
from rest_framework.exceptions import NotFound
from django.db.models import Subquery, OuterRef

from apis.models.member_role import RoleChoices
from apis.models.merchant_member import MerchantMember
from apis.models.merchant_membership import MerchantMembership

from apis.permissions import IsMerchantOrStaff
from apis.serializers.merchant_member import MerchantMemberSerializer


class MerchantMemberListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsMerchantOrStaff]
    serializer_class = MerchantMemberSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "cnic",
        "code",
        "primary_phone",
        "user__first_name",
        "merchant_memberships__secondary_phone",
    ]

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

        # Annotate each member with the active status of their membership with the current merchant
        queryset = MerchantMember.objects.filter(
            memberships__merchant=merchant, roles__role=role
        ).annotate(
            current_active=Subquery(memberships.values("is_active")[:1]),
            area_name=Subquery(memberships.values("area")[:1]),
        )

        return queryset


class MemberRetrieveByPhoneAPIView(generics.RetrieveAPIView):
    permission_classes = [IsMerchantOrStaff]
    serializer_class = MerchantMemberSerializer

    def get_object(self):
        phone = self.kwargs.get("phone")
        try:
            member = MerchantMember.objects.get(primary_phone=phone)
        except MerchantMember.DoesNotExist:
            raise NotFound(detail="Member with this phone number does not exist.")
        return member