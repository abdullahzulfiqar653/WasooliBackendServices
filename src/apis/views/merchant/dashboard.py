from django.utils import timezone
from django.utils.timezone import now
from django.db.models import Sum, Q, Count

from rest_framework import generics
from rest_framework.response import Response

from apis.models.invoice import Invoice
from apis.permissions import IsMerchantOrStaff
from apis.models.transaction_history import TransactionHistory
from apis.serializers.merchant_dashboard import MerchantDashboardSerializer


class MerchantDashboardRetrieveAPIView(generics.RetrieveAPIView):
    """
    **Merchant Dashboard API View**

    ### **Endpoint Description**
    This API retrieves statistics for the merchant's dashboard, including:

    - **Today's collection**: Total amount collected today.
    - **Monthly collection**: Total amount collected this month.
    - **Remaining collection for the month**: Balance collection expected this month.
    - **Yearly collection**: Total amount collected this year.
    - **Total customers**: Number of registered customers.
    - **Active customers**: Number of currently active customers.
    - **Inactive customers**: Number of customers who are not active.

    ### **Request**

    - **Headers**: `Authorization: <your_token>` (Required)\n

    ### **Response**
    - **Status Code**: `200 OK`\n
    - **Response Fields**:\n
      - `key_of_the_card`:\n
        - `value`: integer value for that card.\n
        - `name`:  Name to Display for that card.\n
    """

    permission_classes = [IsMerchantOrStaff]
    serializer_class = MerchantDashboardSerializer

    def retrieve(self, request, *args, **kwargs):
        invoices = Invoice.objects.exclude(status=Invoice.STATUS.CANCELLED)
        today = timezone.now().date()
        current_year = now().year
        current_month = now().month
        first_of_this_month = today.replace(day=1)
        transaction_summary = TransactionHistory.objects.filter(
            merchant_membership__merchant_id=request.merchant.id,  # Filter by merchant ID
            type=TransactionHistory.TYPES.BILLING,
        )
        all_invoices = invoices.filter(
            membership__merchant=request.merchant,  # Filter invoices related to this merchant
        )
        this_month_invoices = invoices.filter(
            membership__merchant=request.merchant,  # Filter invoices related to this merchant
            created_at__year=current_year,
            created_at__month=current_month,
        )
        
        total_this_month = this_month_invoices.aggregate(total_due=Sum("due_amount"), total_amount=Sum("total_amount"))
        total_all_time = all_invoices.aggregate(total_due=Sum("due_amount"), total_amount=Sum("total_amount"))

        total_due_this_month = total_this_month["total_due"] or 0
        total_amount_this_month = total_this_month["total_amount"] or 0
        total_due_all_time = total_all_time["total_due"] or 0


        # Calculate total credit for this merchant_membership
        total_credit = (
            transaction_summary.filter(
                transaction_type=TransactionHistory.TRANSACTION_TYPE.CREDIT
            ).aggregate(total_credit=Sum("value", default=0))["total_credit"]
            or 0
        )

        # Get credit amount for today
        credit_today = (
            transaction_summary.filter(
                transaction_type=TransactionHistory.TRANSACTION_TYPE.CREDIT,
                created_at__date=today,
            ).aggregate(total_credit_today=Sum("value"))["total_credit_today"]
            or 0
        )

        # Get credit amount for this month
        credit_this_month = (
            transaction_summary.filter(
                transaction_type=TransactionHistory.TRANSACTION_TYPE.CREDIT,
                created_at__gte=first_of_this_month,  # Filter from the first day of this month
            ).aggregate(total_credit_this_month=Sum("value"))["total_credit_this_month"]
            or 0
        )

        # Get debit amount for this month
        debit_this_month = (
            transaction_summary.filter(
                transaction_type=TransactionHistory.TRANSACTION_TYPE.DEBIT,
                created_at__gte=first_of_this_month,  # Filter from the first day of this month
            ).aggregate(total_debit_this_month=Sum("value"))["total_debit_this_month"]
            or 0
        )

        # Get adjustment credit amount for this month
        credit_adjustment_this_month = (
            transaction_summary.filter(
                transaction_type=TransactionHistory.TRANSACTION_TYPE.ADJUSTMENT,
                created_at__gte=first_of_this_month,  # Filter from the first day of this month
            ).aggregate(total_credit_adjustment_this_month=Sum("value"))[
                "total_credit_adjustment_this_month"
            ]
            or 0
        )
        total_remaining_collection = (
            debit_this_month - credit_adjustment_this_month - credit_this_month
        )

        membership_aggregates = request.merchant.members.aggregate(
            total_customers=Count("id"),
            active_customers=Count("id", filter=Q(is_active=True)),
            non_active_customers=Count("id", filter=Q(is_active=False)),
        )

        total_customers = membership_aggregates["total_customers"] or 0
        active_customers = membership_aggregates["active_customers"] or 0
        non_active_customers = membership_aggregates["non_active_customers"] or 0
        return Response(
            {
                "total_collections_today": {
                    "value": credit_today,
                    "name": "Collection today",
                },
                "total_collections_this_month": {
                    "value": credit_this_month,
                    "name": "Collection this month",
                },
                "total_remaining_collections_this_month": {
                    "value": total_due_this_month,
                    "name": "Remaining collection this month",
                },
                "total_collections": {
                    "value": total_credit,
                    "name": "Collection this year",
                },
                "total_remaining_collections": {
                    "value": total_due_all_time,
                    "name": "Total Remaining collection",
                },
                "total_customers": {
                    "value": total_customers,
                    "name": "Total Customers",
                },
                "active_customers": {
                    "value": active_customers,
                    "name": "Active Customers",
                },
                "non_active_customers": {
                    "value": non_active_customers,
                    "name": "Non Active Customers",
                },
            }
        )
