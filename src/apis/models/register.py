from django.db import models
from django.contrib.auth.models import User

from apis.models.merchant import Merchant
from apis.models.abstract.base import BaseModel


class RoleChoices(models.TextChoices):
    STAFF = "Staff", "Staff"
    MERCHANT = "Merchant", "Merchant"
    CUSTOMER = "Customer", "Customer"


class Register(BaseModel):
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
    code = models.PositiveIntegerField(unique=True, editable=False)

    def __str__(self):
        return f"{self.user.username} - {self.role.name} of {self.merchant.name}."

    class Meta:
        verbose_name = "MerchantsMembersRegister"
        unique_together = [["user", "merchant", "role", "cnic", "phone"]]

    def save(self, *args, **kwargs):
        if not self.code:  # Auto-generate code only on creation
            last_code = Merchant.objects.aggregate(models.Max("code"))["code__max"]
            self.code = (last_code or 999) + 1
        super().save(*args, **kwargs)
