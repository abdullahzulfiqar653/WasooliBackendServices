from decimal import Decimal
from django.utils import timezone
from rest_framework import generics
from django.db.models import Sum, Q, Count
from rest_framework.response import Response

from apis.permissions import IsMerchantOrStaff
from apis.models.transaction_history import TransactionHistory


class MemberProfileRetrieveAPIView(generics.RetrieveAPIView):
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

        membership = request.merchant.members.filter(member=request.member).first()
        today = timezone.now().date()
        first_of_this_month = today.replace(day=1)
        transaction_summary = membership.membership_transactions.filter(
            type=TransactionHistory.TYPES.BILLING,
        )
        # Calculate total credit amount for transactions of type 'credit'
        total_credit = transaction_summary.filter(
            transaction_type=TransactionHistory.TRANSACTION_TYPE.CREDIT
        ).aggregate(total_credit=Sum("credit", default=Decimal(0)))["total_credit"]

        credit_adjustment = transaction_summary.filter(
            transaction_type=TransactionHistory.TRANSACTION_TYPE.ADJUSTMENT
        ).aggregate(credit_adjustment=Sum("credit", default=Decimal(0)))[
            "credit_adjustment"
        ]

        # Calculate total debit amount
        total_debit = (
            transaction_summary.aggregate(total_debit=Sum("debit", default=Decimal(0)))[
                "total_debit"
            ]
            - credit_adjustment
        )

        # Calculate the remaining debit amount (total debit - total credit)
        remaining_debit = total_debit - total_credit

        return Response(
            {
                "total_spend": {"value": total_credit},
                "total_remaining": {"value": remaining_debit},
                "total_saved": {"value": membership.total_saved},
            }
        )
