from rest_framework import generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed


class RefreshTokenAPIView(generics.RetrieveAPIView):
    permission_classes = []
    serializer_class = None

    def retrieve(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            raise AuthenticationFailed({"detail": "No refresh token found in cookies"})

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response({"access": access_token})
        except Exception as e:
            print(e)
            raise AuthenticationFailed({"detail": "Invalid Refresh Token."})
