from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend

from apis.permissions import IsMerchantOrStaff
from apis.models.transaction_history import TransactionHistory
from apis.serializers.transaction_history import TransactionHistorySerializer

from drf_spectacular.utils import extend_schema


class MemberTransactionHistoryListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = TransactionHistorySerializer
    permission_classes = [IsMerchantOrStaff]
    filter_backends = (DjangoFilterBackend,)
    pagination_class = None
    queryset = TransactionHistory.objects.none()

    def get_queryset(self):
        return self.request.membership.membership_transactions.filter(
            transaction_type=TransactionHistory.TRANSACTION_TYPE.CREDIT,
            type=TransactionHistory.TYPES.BILLING,
        )

    @extend_schema(
        description="""
### List all transaction histories for the member:
This endpoint returns a list of all credit billing transaction histories associated with the member.\n
**Request Parameters**
- `member_id`: The ID of the member .\n
**Response**\n
The response will include the following fields for each transaction:
- `id`: Unique transaction identifier.\n
- `amount`: The amount of the transaction.\n
- `transaction_type`: Type of transaction (e.g., CREDIT).\n
- `type`: The type of transaction (e.g., BILLING).\n
- `created_at`: Timestamp of when the transaction occurred.\n
- `updated_at`: Timestamp of the last update to the transaction.
        """,
        responses={
            200: TransactionHistorySerializer(many=True),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        description="""
### Create a new transaction history record:
- `member_id`: The ID of the member .\n
- `amount`: Amount of the transaction (e.g., 1500).\n
- `transaction_type`: Type of transaction (e.g., CREDIT).\n
- `type`: The type of transaction (e.g., BILLING).\n
- `metadata`: Optional field containing additional information about the transaction.

The request body must contain the above fields. The response will return the newly created transaction history record.
        """,
        request=TransactionHistorySerializer,
        responses={
            201: TransactionHistorySerializer,
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
