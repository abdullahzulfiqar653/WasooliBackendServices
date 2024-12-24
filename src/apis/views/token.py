from rest_framework.generics import CreateAPIView
from apis.serializers.token import TokenSerializer
from apis.permissions import IsMerchantOrStaff


class TokenCreateView(CreateAPIView):
    permission_classes = [IsMerchantOrStaff]
    serializer_class = TokenSerializer
