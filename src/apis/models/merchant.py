from django.db import models
from django.contrib.auth.models import User
from apis.models.abstract.base import BaseModel


class Merchant(BaseModel):
    class MerchantType(models.TextChoices):
        INTERNET = "internet", "Internet"
        WATER = "water", "Water"
        TV = "tv", "TV"
        GYM = "gym", "Gym"
        GARBAGE = "garbage", "Garbage"

    merchant_type = models.CharField(max_length=50, choices=MerchantType.choices)
    owner = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="merchant"
    )
    code = models.PositiveIntegerField(unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.code:  # Auto-generate code only on creation
            last_code = Merchant.objects.aggregate(models.Max("code"))["code__max"]
            self.code = (last_code or 999) + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.code})"
