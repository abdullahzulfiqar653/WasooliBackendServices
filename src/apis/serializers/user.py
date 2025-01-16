from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ["email", "first_name"]
