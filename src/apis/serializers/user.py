from rest_framework import exceptions
from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ["email", "first_name"]

    def validate_email(self, value):
        member = self.context.get("member")
        if member:
            if value is None or member.user.email == value:
                return
            if User.objects.filter(email=value).exclude(id=member.user.id).exists():
                raise serializers.ValidationError("Email already exist.")

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exist.")
        return value
