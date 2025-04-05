from django.db.models import (
    F,
    Sum,
    Value,
    OuterRef,
    Subquery,
    IntegerField,
)
from django.db.models.functions import Coalesce
from apis.models.supply_record import SupplyRecord
from rest_framework import generics

from apis.models.member_role import RoleChoices
from apis.models.merchant_member import MerchantMember

from apis.permissions import IsMerchantOrStaff

from apis.serializers.merchant_member import MerchantMemberSerializer
from apis.serializers.membership_status_change import MembershipStatusChangeSerializer

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
            # Subquery to calculate total given and total taken separately
            membership_supply_balances = (
                SupplyRecord.objects.filter(
                    merchant_membership=OuterRef("memberships__id")
                )
                .values("merchant_membership")
                .annotate(
                    total_given=Sum("given"),
                    total_taken=Sum("taken"),
                )
                .annotate(
                    total_supply_balance=F("total_given") - F("total_taken"),
                )
                .values("total_supply_balance")
            )
            queryset = queryset.annotate(
                supply_balance=Coalesce(
                    Subquery(membership_supply_balances, output_field=IntegerField()),
                    Value(0),
                )
            )
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


class MembershipStatusUpdateApiView(generics.UpdateAPIView):
    """
    This endpoint mark the user as active or  inactive.

    **The payload will include the following fields:**
    - is_active: you can pass true or false to make member active or inactive.

    """

    serializer_class = MembershipStatusChangeSerializer
    permission_classes = [IsMerchantOrStaff]

    def get_object(self):
        return self.request.membership
