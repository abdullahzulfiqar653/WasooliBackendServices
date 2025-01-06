from django.db import models

from apis.models.abstract.base import BaseModel


class SupplyRecord(BaseModel):
    merchant_membership = models.ForeignKey(
        "apis.MerchantMembership",
        on_delete=models.CASCADE,
        related_name="supply_records",
    )
    given = models.SmallIntegerField(default=0)
    taken = models.SmallIntegerField(default=0)

    def __str__(self):
        return f"Supply for {self.merchant_membership.member.user.first_name}"
