import os
import json
import requests

from apis.senders.base import OTPSender
from apis.models.merchant_member import MerchantMember

SMS_OTP_API_KEY = os.getenv("SMS_OTP_API_KEY")


class SmsOTPSender(OTPSender):
    def send_otp(self, member: MerchantMember, otp: str) -> None:
        phone_number = member.primary_phone
        name = member.user.first_name
        message = json.dumps({"name": name, "pin": otp})
        api_url = (
            f"https://sendpk.com/api/sms.php?"
            f"api_key={SMS_OTP_API_KEY}&sender=BrandName&mobile=92{phone_number}"
            f"&template_id=10052&message={message}&format=json"
        )
        response = requests.get(api_url)

        return {
            "message": "OTP sent successfully!",
            "api_response": response.text,
        }
