from datetime import timedelta
from django.utils.timezone import now

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken


from apis.models.otp import OTP
from django.conf import settings
from apis.factories import OTPSenderFactory



class OTPSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    refresh = serializers.CharField(read_only=True)
    access = serializers.CharField(read_only=True)
    message = serializers.CharField(read_only=True)
    remaining_time = serializers.CharField(read_only=True)

    platform = serializers.CharField(default="email", write_only=True)
    otp = serializers.CharField(
        max_length=6, required=False, write_only=True, allow_null=True
    )

    def create(self, validated_data):
        request = self.context.get("request")
        otp_code = validated_data.get("otp")
        platform = validated_data.get("platform", "email")

        if settings.ENV == "DEV":
            if not request.member.id in ["105fBHTSGRRM38d", "105LevvX8Q7gziD", "105jfY4tyo8vXqc"]:
                platform = "email"

        if otp_code:
            try:
                otp_record = request.member.otp
            except OTP.DoesNotExist:
                raise ValidationError({"otp": ["Invalid OTP"]})

            if otp_record.code != otp_code:
                raise ValidationError({"otp": ["Invalid OTP"]})

            if not otp_record.is_valid():
                raise ValidationError({"otp": ["OTP expired"]})

            refresh = RefreshToken.for_user(request.member.user)
            # otp_record.is_used = True
            # otp_record.save()
            return {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }

        else:
            otp_record, created = OTP.objects.get_or_create(member=request.member)
            if not created and otp_record.updated_at >= now() - timedelta(minutes=2):
                remaining_time = 120 - (now() - otp_record.updated_at).seconds
                return {"message": "Please wait 2 minutes before trying again.", "remaining_time": remaining_time}

            otp = otp_record.generate_otp()
            sender = OTPSenderFactory.get_sender(platform)
            sender.send_otp(request.member, otp)

            return {"message": "OTP sent successfully!"}
