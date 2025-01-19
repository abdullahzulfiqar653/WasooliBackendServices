from apis.serializers.otp import OTPSerializer
from rest_framework.generics import CreateAPIView
from apis.permissions import IsMerchantMemberAnonymous


class OTPView(CreateAPIView):
    serializer_class = OTPSerializer
    permission_classes = [IsMerchantMemberAnonymous]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        refresh_token = response.data.get("refresh")
        response.set_cookie("refresh_token", refresh_token, httponly=True, secure=True)

        return response
