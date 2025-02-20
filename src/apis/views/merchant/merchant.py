from django.utils import timezone
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
        is_paid = self.request.query_params.get("is_paid", None)
        is_paid_today = self.request.query_params.get("is_paid_today", None)
        merchant = self.request.merchant

        merchant_member_queryset = MerchantMember.objects.filter(
            roles__role__in=[
                RoleChoices.STAFF,
                RoleChoices.CUSTOMER,
                RoleChoices.MERCHANT,
            ]
        )

        # Conditionally add the filter based on the role
        if role == RoleChoices.STAFF:
            merchant_member_queryset = merchant.staff_members.exclude(
                user=self.request.user
            )  # For STAFF, use `merchant=merchant`
        else:
            merchant_member_queryset = merchant_member_queryset.filter(
                memberships__merchant=merchant
            )  # For CUSTOMER, use `memberships__merchant=merchant`
            # Annotate total_credit, total_debit, and total_adjustment
            transaction_history_queryset = TransactionHistory.objects.filter(
                merchant_membership__in=merchant_member_queryset.values(
                    "memberships__id"
                ),
                type=TransactionHistory.TYPES.BILLING,
            )

            merchant_member_queryset = merchant_member_queryset.prefetch_related(
                Prefetch(
                    "memberships__membership_transactions",
                    queryset=transaction_history_queryset,
                )
            )

            today = timezone.now().date()
            transaction_history_queryset_today = transaction_history_queryset.filter(
                created_at__date=today,
                transaction_type=TransactionHistory.TRANSACTION_TYPE.CREDIT,
            )

            # Annotate total_credit, total_debit, and total_adjustment
            merchant_member_queryset = merchant_member_queryset.annotate(
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
            if is_paid == "true":
                merchant_member_queryset = merchant_member_queryset.filter(
                    balance__gte=0
                )
            if is_paid == "false":
                merchant_member_queryset = merchant_member_queryset.filter(
                    balance__lt=0
                )
            if is_paid_today == "true":
                merchant_member_queryset = merchant_member_queryset.filter(
                    memberships__membership_transactions__in=transaction_history_queryset_today
                )

        return merchant_member_queryset.order_by("-code")

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="role",
                description="Filter members by their role",
                required=False,
                type=OpenApiTypes.STR,
                enum=[RoleChoices.STAFF],
            ),
            OpenApiParameter(
                name="is_paid",
                description="Filter members by their paid or unpaid status",
                required=False,
                type=OpenApiTypes.STR,
                enum=["true", "false"],
            ),
            OpenApiParameter(
                name="is_paid_today",
                description="Filter members who paid today",
                required=False,
                type=OpenApiTypes.STR,
                enum=["true"],
            ),
        ],
        description="""
### **Retrieve List of Merchant Members**

This API returns a list of merchant members (either Staff or Customers).

- `For Staff`: Include the parameter `role=Staff` to retrieve staff members. Staff members will be returned with no membership data.\n
- `For Customers`: No additional parameters are required to retrieve customer details. Customer members will be returned with their membership details

""",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        description="""
### **Create Merchant Member**

This API allows the creation of a new merchant member, either **Staff** or **Customer**.

- **For Staff:** `merchant_memberships` should be set to `null`.\n
- **For Customers:** `merchant_memberships` is required.

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

    @extend_schema(
        description="""
### **🔍 Retrieve Member by Phone Number & Merchant ID**

- This view retrieves a member based on their primary phone number to assist merchants when
    creating a new customer or staff.
- If the primary phone number already exists, the member's data will be pre-populated in the
    creation form for convenience.

#### **🟢 Request Parameters (Path)**
| Parameter    | Required | Description |
|--------------|----------|-------------|
| `merchant_id`      | ✅ Yes   | The merchant_id of the merchant
| `phone`      | ✅ Yes   | The primary phone number of the member
---

""",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
