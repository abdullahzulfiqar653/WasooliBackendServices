from rest_framework.generics import CreateAPIView
from apis.serializers.token import TokenSerializer
from apis.permissions import IsAllowedToLogin


class TokenCreateView(CreateAPIView):
    permission_classes = [IsAllowedToLogin]
    serializer_class = TokenSerializer
