from django.db import models
from datetime import timedelta
from django.utils.timezone import now
from apis.models.abstract.base import BaseModel
from apis.models.merchant_member import MerchantMember


class OTP(BaseModel):
    member = models.OneToOneField(
        MerchantMember, on_delete=models.CASCADE, related_name="otp"
    )
    code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)

    def is_valid(self) -> bool:
        """Check if the OTP is valid based on time and usage."""
        return not self.is_used and now() < self.updated_at + timedelta(minutes=5)
