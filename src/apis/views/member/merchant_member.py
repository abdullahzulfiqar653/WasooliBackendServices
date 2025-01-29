from rest_framework import generics

from apis.models.member_role import RoleChoices
from apis.models.merchant_member import MerchantMember

from apis.permissions import IsMerchantOrStaff
from apis.serializers.merchant_member import MerchantMemberSerializer


class MemberRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    This view to retrive, update and delete merchant members wether `Staff` or `Customers`.
    - `For Staff`:
    - To retrieve staff member, include the parameter `role=Staff` in the request.
    - To update a staff member, set `merchant_memberships` to `null`.
    - `For Customers`:
    - No additional parameters are required to retrieve customer.
    - The `merchant_memberships` field is required when updating a customer.

    - `To Delete`: Only `merchant` can delete members and just `member_id` is needed.
    """

    permission_classes = [IsMerchantOrStaff]
    serializer_class = MerchantMemberSerializer

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
        queryset = queryset.distinct()
        return queryset
