from rest_framework import generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from apis.serializers.refresh_token import RefreshTokenSerializer


class RefreshTokenAPIView(generics.RetrieveAPIView):
    """
    - If you are logged in successfully, the refresh token is stored in HTTP-only cookies.
    - To obtain an access token, simply send a GET request to this endpoint from the same origin.
    - The access token will be returned in the response.
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
