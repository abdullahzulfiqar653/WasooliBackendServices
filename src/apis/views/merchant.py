from rest_framework import generics, filters
from rest_framework.exceptions import NotFound

from apis.models.member_role import RoleChoices
from apis.models.merchant_member import MerchantMember

from apis.permissions import IsMerchantOrStaff
from apis.serializers.merchant_member import MerchantMemberSerializer


class MerchantMemberListCreateAPIView(generics.ListCreateAPIView):
    """
    This view handles listing and creating merchant members.
    - `For Staff`:
    - To list staff members, include the parameter `role=Staff` in the request.
    - To create a staff member, set `merchant_memberships` to `null`.
    - `For Customers`:
    - No additional parameters are required to list them.
    - The `merchant_memberships` field is required when creating a customer.
    """

    permission_classes = [IsMerchantOrStaff]
    serializer_class = MerchantMemberSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["cnic", "code", "primary_phone", "user__first_name"]

    def get_queryset(self):
        role = self.request.query_params.get("role", RoleChoices.CUSTOMER)
        merchant = self.request.user.merchant

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

        return queryset.order_by("-code")


class MemberRetrieveByPhoneAPIView(generics.RetrieveAPIView):
    """
    - This view retrieves a member based on their primary phone number to assist merchants when
    creating a new customer or staff.
    - If the primary phone number already exists, the member's data will be pre-populated in the
    creation form for convenience.
    """

    permission_classes = [IsMerchantOrStaff]
    serializer_class = MerchantMemberSerializer

    def get_object(self):
        phone = self.kwargs.get("phone")
        try:
            member = MerchantMember.objects.get(primary_phone=phone)
        except MerchantMember.DoesNotExist:
            raise NotFound(detail="Member with this phone number does not exist.")
        return member
