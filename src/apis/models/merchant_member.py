from django.db import models
from django.contrib.auth.models import User

from apis.models.merchant import Merchant
from apis.models.abstract.base import BaseModel


class RoleChoices(models.TextChoices):
    STAFF = "Staff", "Staff"
    MERCHANT = "Merchant", "Merchant"
    CUSTOMER = "Customer", "Customer"


class MerchantMember(BaseModel):
    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, related_name="profile", null=True
    )
    memberships = models.ManyToManyField(
        "apis.Merchant", through="MerchantMembership", related_name="users"
    )
    role = models.CharField(
        max_length=50, choices=RoleChoices.choices, default=RoleChoices.CUSTOMER
    )
    cnic = models.CharField(max_length=13, null=True)
    picture = models.ImageField(upload_to="protected/picture", null=True)
    primary_phone = models.CharField(
        max_length=10, null=True, verbose_name="Primary Phone", unique=True
    )

    class Meta:
        verbose_name = "MerchantsMembersRegister"
        unique_together = [["user", "role", "cnic", "primary_phone"]]

    def __str__(self):
        return f"{self.user.username} - {self.role.name} of {self.merchant.name}."
