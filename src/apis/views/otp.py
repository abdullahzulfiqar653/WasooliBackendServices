from apis.serializers.otp import OTPSerializer
from rest_framework.generics import CreateAPIView
from apis.permissions import IsMerchantMemberAnonymous


class OTPView(CreateAPIView):
    """
    This view accepts three body parameters: `username`, `otp`, and `platform`.

    - `platform`: Can be one of `email`, `whatsapp`, or `sms`. Use this to specify the medium for OTP delivery.
    - `username`: Provide the corresponding value (e.g., email address or phone number) based on the chosen platform.
    - `otp`: Initially, set this to `null`. When user receives the OTP, resend request including received `otp`.

    If the OTP validation is successful, an access token will be returned. Otherwise, you will receive OTP-related errors.
    """

    serializer_class = OTPSerializer
    permission_classes = [IsMerchantMemberAnonymous]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        refresh_token = response.data.pop("refresh", None)
        response.set_cookie(
            "wasooli_refresh_token", refresh_token, httponly=True, secure=True
        )
        return response
