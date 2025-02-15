from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from apis.models.supply_record import SupplyRecord
from apis.models.transaction_history import TransactionHistory


def get_customer_stats(membership):
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
    user_amounts_balance = total_credit - total_debit
    response = {
        "total_spend": {"value": total_credit, "name": "Total Spend"},
        "user_amounts_balance": {"value": user_amounts_balance, "name": "Balance"},
        "total_saved": {"value": membership.total_saved, "name": "Total Saved"},
    }
    if not membership.merchant.is_fixed_fee_merchant:
        if not membership.is_monthly:
            supply_totals = SupplyRecord.objects.filter(
                merchant_membership=membership
            ).aggregate(total_given=Sum("given"), total_taken=Sum("taken"))

            # If no supply records exist, set defaults to 0
            total_given = supply_totals.get("total_given", 0)
            total_taken = supply_totals.get("total_taken", 0)

            # Calculate the balance
            supply_balance = total_given - total_taken
            response["supply_balance"] = {
                "value": supply_balance,
                "name": "Supply Balance",
            }
            if membership.merchant.is_water_supply:
                response["supply_balance"]["name"] = "Bottles Balance"
    return response
