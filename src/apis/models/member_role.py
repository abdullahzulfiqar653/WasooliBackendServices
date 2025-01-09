from django.db import models
from apis.models.abstract.base import BaseModel


class RoleChoices(models.TextChoices):
    STAFF = "Staff", "Staff"
    MERCHANT = "Merchant", "Merchant"
    CUSTOMER = "Customer", "Customer"


class MemberRole(BaseModel):
    member = models.ForeignKey(
        "apis.MerchantMember", on_delete=models.CASCADE, related_name="roles"
    )
    role = models.CharField(max_length=20, choices=RoleChoices.choices)

    def __str__(self):
        return f"{self.member.user.username} - {self.role}"
