from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend

from apis.permissions import IsMerchantOrStaff
from apis.models.transaction_history import TransactionHistory
from apis.serializers.transaction_history import TransactionHistorySerializer

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter


class MemberTransactionHistoryListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = TransactionHistorySerializer
    permission_classes = [IsMerchantOrStaff]
    filter_backends = (DjangoFilterBackend,)
    pagination_class = None
    queryset = TransactionHistory.objects.none()

    def get_queryset(self):
        return self.request.membership.membership_transactions.all()
