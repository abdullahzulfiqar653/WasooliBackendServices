from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    refresh = serializers.CharField(read_only=True)
    access = serializers.CharField(read_only=True)

    class Meta:
        fields = ["username", "password"]

    def validate_password(self, password):
        request = self.context.get("request")
        if not request.user.check_password(password):
            raise ValidationError("Incorrect password.")
        return password

    def create(self, validated_data):
        request = self.context.get("request")
        refresh = RefreshToken.for_user(request.user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
