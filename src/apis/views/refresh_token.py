from rest_framework import generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from apis.serializers.refresh_token import RefreshTokenSerializer


class RefreshTokenAPIView(generics.RetrieveAPIView):
    """
    This endpoint allows users to refresh their **access token** using the **refresh token** stored in HTTP-only cookies.

    **How It Works:**
    - When a user logs in successfully, the `refresh_token` is stored in the browser’s **HTTP-only cookies**.

    - To get a new **access token**, the client should send a **GET request** to this endpoint.

    - If the request is from the **same origin** and includes the stored **refresh token**, a new access token will be returned.

    **Request:**
    - This is a `GET` request.

    - No body parameters are required.

    - Requires a valid `refresh_token` stored in HTTP-only cookies.

    **Response:**
    - If successful, returns a new **access token**.
    - If the refresh token is missing or invalid, an authentication error is raised.
    """

    permission_classes = []
    serializer_class = RefreshTokenSerializer

    def retrieve(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("wasooli_refresh_token")
        if not refresh_token:
            raise AuthenticationFailed({"detail": "No refresh token found in cookies"})

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response({"access": access_token})
        except Exception as e:
            print(e)
            raise AuthenticationFailed({"detail": "Invalid Refresh Token."})
