from rest_framework import generics
from rest_framework.exceptions import NotFound

from apis.permissions import IsMerchantOrStaff
from apis.serializers.transaction_history import TransactionHistorySerializer

from drf_spectacular.utils import extend_schema


class TransactionHistoryUpdateAPIView(generics.UpdateAPIView):
    permission_classes = [IsMerchantOrStaff]
    serializer_class = TransactionHistorySerializer

    def get_object(self):
        """
        Overriding get_object to ensure only the most recent credit transaction is updated.
        """
        from apis.models.transaction_history import TransactionHistory

        # Use the `latest()` method to get the most recent credit transaction
        try:
            latest_credit_transaction = (
                self.request.membership.membership_transactions.filter(
                    transaction_type=TransactionHistory.TRANSACTION_TYPE.CREDIT
                ).latest()
            )
        except TransactionHistory.DoesNotExist:
            raise NotFound({"detail": "No credit transactions found."})

        # Check if the requested transaction is the most recent credit transaction
        if self.kwargs.get("pk") != latest_credit_transaction.id:
            raise NotFound(
                {"detail": "You can only update the most recent credit transaction."}
            )
        return latest_credit_transaction

    @extend_schema(
        description="""
            This API revert the transaction apply the new amount
        """,
        responses={200: TransactionHistorySerializer()},
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
