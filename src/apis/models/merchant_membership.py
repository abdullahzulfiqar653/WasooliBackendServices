from django.db import models
from django.contrib.auth.models import User

from apis.models.abstract.base import BaseModel


class MerchantMembership(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="merchant_memberships"
    )
    merchant = models.ForeignKey(
        "apis.Merchant", on_delete=models.CASCADE, related_name="memberships"
    )
    is_active = models.BooleanField(default=True)
    address = models.TextField(null=True)
    area = models.ForeignKey(
        "apis.Lookup",
        on_delete=models.SET_NULL,
        related_name="merchant_memberships",
        null=True,
    )
    city = models.ForeignKey(
        "apis.Lookup",
        on_delete=models.SET_NULL,
        related_name="merchant_memberships",
        null=True,
    )
    secondary_phone = models.CharField(max_length=10, null=True)

    class Meta:
        unique_together = ["user", "merchant"]

    def __str__(self):
        return (
            f"{self.user.username} - {self.user.profile.role} of {self.merchant.name}."
        )
