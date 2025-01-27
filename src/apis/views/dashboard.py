from django.utils import timezone
from django.db.models import Sum, Q, Count

from rest_framework import generics
from rest_framework.response import Response

from apis.permissions import IsMerchantOrStaff
from apis.models.transaction_history import TransactionHistory


class DashboardRetrieveAPIView(generics.RetrieveAPIView):
    """
    This endpoint provides all the information for dashboard cards:
    - Example response structure:
        {
            "active_users": {"value": 40}
        }

    - It includes metrics such as:
        - Total collections today
        - Total collections this month
        - Total remaining collections this month
        - Total customers
        - Active and non-active customers
        - Earnings this month
        - Active users
    """

    permission_classes = [IsMerchantOrStaff]
    serializer_class = None

    def retrieve(self, request, *args, **kwargs):
        today = timezone.now().date()
        first_of_this_month = today.replace(day=1)
        transaction_summary = TransactionHistory.objects.filter(
            merchant_membership__merchant_id=request.merchant.id,  # Filter by merchant ID
            type=TransactionHistory.TYPES.BILLING,
        )

        # Aggregate the sums for the specified merchant
        merchant_transaction_sums = transaction_summary.aggregate(
            total_credit=Sum("credit"),
            total_debit=Sum("debit"),
            total_credit_adjustment=Sum(
                "credit",
                filter=Q(
                    transaction_type=TransactionHistory.TRANSACTION_TYPE.ADJUSTMENT
                ),
            ),
        )

        # Calculate the adjusted total debit
        total_credit_adjustment = (
            merchant_transaction_sums["total_credit_adjustment"] or 0
        )
        total_credit = (
            merchant_transaction_sums["total_credit"] or 0
        ) - total_credit_adjustment

        # Get credit amount for today
        credit_today = (
            transaction_summary.filter(
                transaction_type=TransactionHistory.TRANSACTION_TYPE.CREDIT,
                created_at__date=today,
            ).aggregate(total_credit_today=Sum("credit"))["total_credit_today"]
            or 0
        )

        # Get credit amount for this month
        credit_this_month = (
            transaction_summary.filter(
                transaction_type=TransactionHistory.TRANSACTION_TYPE.CREDIT,
                created_at__gte=first_of_this_month,  # Filter from the first day of this month
            ).aggregate(total_credit_this_month=Sum("credit"))[
                "total_credit_this_month"
            ]
            or 0
        )

        # Get debit amount for this month
        debit_this_month = (
            transaction_summary.filter(
                transaction_type=TransactionHistory.TRANSACTION_TYPE.DEBIT,
                created_at__gte=first_of_this_month,  # Filter from the first day of this month
            ).aggregate(total_debit_this_month=Sum("debit"))["total_debit_this_month"]
            or 0
        )

        # Get adjustment credit amount for this month
        credit_adjustment_this_month = (
            transaction_summary.filter(
                transaction_type=TransactionHistory.TRANSACTION_TYPE.ADJUSTMENT,
                created_at__gte=first_of_this_month,  # Filter from the first day of this month
            ).aggregate(total_credit_adjustment_this_month=Sum("credit"))[
                "total_credit_adjustment_this_month"
            ]
            or 0
        )
        remaining_debit_this_month = (
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
                "total_collections_today": {"value": credit_today},
                "total_collections_this_month": {"value": credit_this_month},
                "total_remaining_collections_this_month": {
                    "value": remaining_debit_this_month
                },
                "total_collections": {"value": total_credit},
                "total_remaining_collections": {"value": total_credit},
                "total_customers": {"value": total_customers},
                "active_customers": {"value": active_customers},
                "non_active_customers": {"value": non_active_customers},
            }
        )
