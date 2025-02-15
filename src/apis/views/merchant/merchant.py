from rest_framework import generics, filters
from rest_framework.exceptions import NotFound
from django.db.models import F, Sum, Case, When, Value, Prefetch, DecimalField

from apis.models.member_role import RoleChoices
from apis.models.merchant_member import MerchantMember
from apis.models.transaction_history import TransactionHistory

from apis.permissions import IsMerchantOrStaff
from apis.serializers.merchant_member import MerchantMemberSerializer

from drf_spectacular.utils import extend_schema


class MerchantMemberListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsMerchantOrStaff]
    serializer_class = MerchantMemberSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["cnic", "code", "primary_phone", "user__first_name"]

    def get_queryset(self):
        role = self.request.query_params.get("role", RoleChoices.CUSTOMER)
        is_paid = self.request.query_params.get("is_paid", None)
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
            if is_paid == "true":
                queryset = queryset.filter(balance__gte=0)
            elif is_paid == "false":
                queryset = queryset.filter(balance__lt=0)
        return queryset.order_by("-code")

    @extend_schema(
        description="""
### **Retrieve List of Merchant Members**

This API returns a list of merchant members (either Staff or Customers).

---

#### **Request Parameters**
| Parameter  | Required | Description |
|------------|----------|-------------|
| `merchant_id`| ✅ Yes   | The ID of the merchant. |


---

### **Status Codes**
| Code  | Description |
|-------|-------------|
| `200 OK` | Successful response with member list. |
| `403 Forbidden` | Access denied (if the user is not authorized). |
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

---

### **Permissions**
- This API is restricted to **merchants and staff** (`IsMerchantOrStaff` permission class).

### **Status Codes**
| Code  | Description |
|-------|-------------|
| `201 Created` | Successfully created a merchant member. |
| `400 Bad Request` | Validation errors or missing fields. |
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

This API retrieves a **merchant member's details** based on their **primary phone number** and **merchant ID**.

#### **🟢 Request Parameters (Path)**
| Parameter    | Required | Description |
|--------------|----------|-------------|
| `merchant_id`| ✅ Yes   | The ID of the merchant. |
| `phone`      | ✅ Yes   | The primary phone number of the merchant member
---

### **📌 Response Headers (Fields Explanation)**

| Field             | Description |
|-------------------|-------------|
| `id`              |  Unique identifier of the merchant member. |
| `user.email`      | Email address of the user. |
| `user.first_name` | First name of the user. |
| `cnic`            | National identity card number of the member. |
| `code`            | Unique membership code. |
| `picture`         | Profile picture URL of the user. |
| `balance`         | Wallet balance of the merchant member. |
| `primary_phone`   | Primary contact number of the merchant member. |
| `merchant_memberships.area`  | The area where the merchant is located. |
| `merchant_memberships.city`  | The city of the merchant. |
| `merchant_memberships.unit`  | Business unit name or identifier. |
| `merchant_memberships.picture`  | Business logo or profile picture URL. |
| `merchant_memberships.address`  | Business address of the merchant. |
| `merchant_memberships.merchant` | Name of the merchant. |
| `merchant_memberships.is_active`| Indicates if the membership is active. |
| `merchant_memberships.meta_data`  | Additional metadata related to the merchant membership. |
| `merchant_memberships.is_monthly` | Indicates if the membership is on a monthly basis. |
| `merchant_memberships.actual_price` | Original price of the membership. |
| `merchant_memberships.secondary_phone`  | Secondary phone number of the merchant member. |
| `merchant_memberships.discounted_price` |  Discounted price after applying offers. |

---

### **Status Codes**
| Code  | Description |
|-------|-------------|
| `200 OK` | Successfully retrieved member details. |
| `404 Not Found` | If no member exists with the given phone number. |
""",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
