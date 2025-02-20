from rest_framework import generics

from apis.models.member_role import RoleChoices
from apis.models.merchant_member import MerchantMember

from apis.permissions import IsMerchantOrStaff
from apis.serializers.merchant_member import MerchantMemberSerializer

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter


class MemberRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsMerchantOrStaff]
    serializer_class = MerchantMemberSerializer

    def get_queryset(self):
        role = self.request.query_params.get("role", RoleChoices.CUSTOMER)
        merchant = self.request.merchant

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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="role",
                description="Filter members by their role",
                required=False,
                type=OpenApiTypes.STR,
                enum=[RoleChoices.STAFF],
            )
        ],
        description="""
    This endpoint retrieves details of a merchant member.
    
- `For Staff`: Include the parameter `role=Staff` to retrieve staff members.\n
- `For Customers`: No additional parameters are required to retrieve customer details.
        """,
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        description="""
    This endpoint updates details of a merchant member.
    
- `For Staff`: To update staff members, set `merchant_memberships` to `null`.\n
- `For Customers`: You must include the `merchant_memberships` field when updating customer details.
        """
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        description="""
This endpoint deletes a merchant member.
- Only a merchant can delete members.
        """
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
