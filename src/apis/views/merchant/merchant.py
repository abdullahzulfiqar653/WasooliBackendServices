from django.utils import timezone
from rest_framework import generics, filters
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from django.db.models import (
    F,
    Sum,
    Case,
    When,
    Value,
    Subquery,
    OuterRef,
    DecimalField,
)

from apis.models.merchant import Merchant
from apis.models.member_role import RoleChoices
from apis.models.merchant_member import MerchantMember
from apis.models.transaction_history import TransactionHistory

from apis.permissions import IsMerchantOrStaff
from apis.serializers.merchant_member import MerchantMemberSerializer
from apis.serializers.merchant_footer import MerchantFooterSerializer
from apis.serializers.generate_invoice import GenerateInvoicesSerializer

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse


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
            merchant_member_queryset = merchant.staff_members.select_related(
                "otp"
            ).exclude(
                user=self.request.user
            )  # For STAFF, use `merchant=merchant`
        else:
            # For CUSTOMER, use memberships filtering
            merchant_member_queryset = merchant_member_queryset.filter(
                memberships__merchant=merchant
            ).distinct()

            # Annotate total_credit, total_debit, and total_adjustment for memberships
            transaction_history_queryset = TransactionHistory.objects.filter(
                merchant_membership__merchant=merchant,
                type=TransactionHistory.TYPES.BILLING,
            )

            today = timezone.now().date()
            transaction_history_queryset_today = transaction_history_queryset.filter(
                created_at__date=today,
                transaction_type=TransactionHistory.TRANSACTION_TYPE.CREDIT,
            )

            # Now annotate balances directly on the membership
            # For each membership, calculate balance by summing debits, credits, and adjustments
            membership_balance_subquery = (
                TransactionHistory.objects.filter(
                    merchant_membership=OuterRef("memberships__id"),
                    type=TransactionHistory.TYPES.BILLING,
                )
                .values("merchant_membership")
                .annotate(
                    total_credit=Sum(
                        Case(
                            When(
                                transaction_type=TransactionHistory.TRANSACTION_TYPE.CREDIT,
                                then=F("value"),
                            ),
                            default=Value(0),
                            output_field=DecimalField(),
                        )
                    ),
                    total_debit=Sum(
                        Case(
                            When(
                                transaction_type=TransactionHistory.TRANSACTION_TYPE.DEBIT,
                                then=F("value"),
                            ),
                            default=Value(0),
                            output_field=DecimalField(),
                        )
                    ),
                    total_adjustment=Sum(
                        Case(
                            When(
                                transaction_type=TransactionHistory.TRANSACTION_TYPE.ADJUSTMENT,
                                then=F("value"),
                            ),
                            default=Value(0),
                            output_field=DecimalField(),
                        )
                    ),
                )
                .annotate(
                    balance=F("total_credit")
                    - (F("total_debit") - F("total_adjustment"))
                )
                .values("balance")
            )

            merchant_member_queryset = merchant_member_queryset.annotate(
                balance=Subquery(
                    membership_balance_subquery, output_field=DecimalField()
                )
            )

            # Filter by paid/unpaid balances
            if is_paid == "true":
                merchant_member_queryset = merchant_member_queryset.filter(
                    balance__gte=0
                )
            elif is_paid == "false":
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


class MerchantFooterRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """
    This API allows merchants to retrieve and update their footer metadata.
    The metadata is stored as a JSON field containing a list of key-value pairs.
    """

    permission_classes = [IsMerchantOrStaff]
    serializer_class = MerchantFooterSerializer

    def get_queryset(self):
        return Merchant.objects.filter(id=self.kwargs["pk"])

    @extend_schema(
        description="Retrieve the footer metadata of the merchant.",
        responses={
            200: {
                "description": "Successful response",
                "content": {
                    "application/json": {
                        "example": {
                            "metadata": {
                                "phone": "3103987654",
                                "address": "Gulshan Usman",
                                "note": "We are open 24/7",
                            }
                        }
                    }
                },
            }
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        description="Update the footer metadata of the merchant with key-value pairs.",
        request={
            "application/json": {
                "example": {
                    "metadata": {
                        "phone": "3103987654",
                        "address": "Gulshan Usman",
                        "note": "We are open 24/7",
                    }
                }
            }
        },
        responses={
            200: {
                "description": "Metadata updated successfully",
                "content": {
                    "application/json": {
                        "example": {
                            "metadata": {
                                "footer": {
                                    "phone": "3103987654",
                                    "address": "Gulshan Usman",
                                    "note": "We are open 24/7",
                                }
                            }
                        }
                    }
                },
            }
        },
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)


class GenerateInvoicesAPIView(generics.CreateAPIView):
    serializer_class = GenerateInvoicesSerializer
    permission_classes = [IsMerchantOrStaff]

    @extend_schema(
        description="""
        ### Generate Invoices:
        - This API allows merchants to generate invoices for all members.
        - Invoices are created based on the member's billing type (monthly or supply-based).
        - The response includes the generated invoices with their details.
        """,
        request=GenerateInvoicesSerializer,
        responses={
            201: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Invoices created successfully",
            ),
            400: OpenApiResponse(description="Bad Request - Invalid data"),
        },
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.save()

        return Response(data, status=201)
