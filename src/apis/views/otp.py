from apis.serializers.otp import OTPSerializer
from rest_framework.generics import CreateAPIView
from apis.permissions import IsMerchantMemberAnonymous


class OTPView(CreateAPIView):
    """
    Handles OTP (One-Time Password) authentication for user verification.

    **Request Body Parameters:**

    - `platform` (**required**): The method used to send the OTP. Accepted values: `email`, `whatsapp`, `sms`.

    - `username` (**required**): The recipient's email or phone number where the OTP is sent.

    - `otp` : The OTP received by the user. Initially, this should be `null`. Once the user receives an OTP, they must resend the request including the received OTP.

    **Workflow:**
    1. User sends a request with `platform` and `username`, setting `otp` to `null`.

    2. System sends an OTP via the specified `platform`.

    3. User resends the request, this time including the received `otp`.

    4. If the OTP is valid, the system returns an access token and sets a secure HTTP-only refresh token.

    **Response:**
      - `access` : A JWT access token that allows the user to authenticate further requests.

    **Security Measures:**
    - The refresh token is set in an HTTP-only, secure cookie to prevent XSS attacks.
    - JWT authentication is used for secure access token management.
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
