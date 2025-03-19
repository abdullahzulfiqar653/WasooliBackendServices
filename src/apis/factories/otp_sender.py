from apis.senders.sms_sender import SmsOTPSender
from apis.senders.email_sender import EmailOTPSender
from apis.senders.whatsapp_sender import WhatsAppOTPSender


class OTPSenderFactory:
    @staticmethod
    def get_sender(platform: str):
        if platform == "email":
            return EmailOTPSender()
        elif platform == "whatsapp":
            return WhatsAppOTPSender()
        elif platform == "sms":
            return SmsOTPSender()
        else:
            raise ValueError(f"Unsupported platform: {platform}")
