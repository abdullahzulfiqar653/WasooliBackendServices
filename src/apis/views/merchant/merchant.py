from rest_framework import generics, filters
from rest_framework.exceptions import NotFound
from django.db.models import F, Sum, Case, When, Value, Prefetch, DecimalField

from apis.models.member_role import RoleChoices
from apis.models.merchant_member import MerchantMember
from apis.models.transaction_history import TransactionHistory

from apis.permissions import IsMerchantOrStaff
from apis.serializers.merchant_member import MerchantMemberSerializer

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter


class MerchantMemberListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsMerchantOrStaff]
    serializer_class = MerchantMemberSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["cnic", "code", "primary_phone", "user__first_name"]

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
            # Annotate total_credit, total_debit, and total_adjustment
            transaction_history_queryset = TransactionHistory.objects.filter(
                merchant_membership__in=queryset.values("memberships__id"),
                type=TransactionHistory.TYPES.BILLING,
            )
            queryset = queryset.prefetch_related(
                Prefetch(
                    "memberships__membership_transactions",
                    queryset=transaction_history_queryset,
                )
            )

            # Annotate total_credit, total_debit, and total_adjustment
            queryset = queryset.annotate(
                total_credit=Sum(
                    Case(
                        When(
                            memberships__membership_transactions__transaction_type=TransactionHistory.TRANSACTION_TYPE.CREDIT,
                            then=F("memberships__membership_transactions__credit"),
                        ),
                        default=Value(0),
                        output_field=DecimalField(),
                    )
                ),
                total_debit=Sum(
                    "memberships__membership_transactions__debit", default=0
                ),
                total_adjustment=Sum(
                    Case(
                        When(
                            memberships__membership_transactions__transaction_type=TransactionHistory.TRANSACTION_TYPE.ADJUSTMENT,
                            then=F("memberships__membership_transactions__credit"),
                        ),
                        default=Value(0),
                        output_field=DecimalField(),
                    )
                ),
            ).annotate(
                balance=F("total_credit") - (F("total_debit") - F("total_adjustment"))
            )
        return queryset.order_by("-code")

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
        \nThis view handles listing of merchant members.
            \n- `For Staff`: Include the parameter `role=Staff` to list staff members.
            \n- `For Customers`: No additional parameters are required to list them.""",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        description="""
        \nThis view handles creating merchant members wether Staff or Customer.
        \n- `For Staff`: Set `merchant_memberships` to `null` to create a staff member.
        \n- `For Customers`: The `merchant_memberships` field is required when creating a customer.
        """,
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


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
