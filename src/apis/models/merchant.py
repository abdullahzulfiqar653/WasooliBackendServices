from django.db import models
from django.contrib.auth.models import User
from apis.models.abstract.base import BaseModel


class Merchant(BaseModel):
    class MerchantType(models.TextChoices):
        TV = "tv", "TV"
        GYM = "gym", "Gym"
        MILK = "milk", "Milk"
        WATER = "water", "Water"
        GARBAGE = "garbage", "Garbage"
        INTERNET = "internet", "Internet"
        Installment = "installment", "Installment"

    name = models.CharField(max_length=50)
    type = models.CharField(max_length=50, choices=MerchantType.choices)
    owner = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="merchant"
    )
    code = models.CharField(max_length=6, unique=True, editable=False)
    commission_structure = models.JSONField(
        default=lambda: {
            "cash": [
                {"max_credit": 1000, "commission": 0.1},
                {"max_credit": 2000, "commission": 0.2},
                {"max_credit": 3000, "commission": 0.3},
                {"max_credit": 4000, "commission": 0.4},
                {"max_credit": 5000, "commission": 0.5},
            ],
            "online": [{"max_credit": 1000, "commission": 0.5}],
        },
        help_text="""Stores commission tiers for cash and online transactions. Example: 
            {
                "cash": [
                    {"max_credit": 1000, "commission": 1},
                    {"max_credit": 3000, "commission": 3},
                    {"max_credit": 5000, "commission": 5}
                ],
                "online": [
                    {"max_credit": 1000, "commission": 2},
                    {"max_credit": 3000, "commission": 5},
                    {"max_credit": 5000, "commission": 8}
                ]
            }
        """,
    )

    def __str__(self):
        return f"{self.name} ({self.code})"

    def save(self, *args, **kwargs):
        if not self.code:
            last_code = Merchant.objects.aggregate(models.Max("code"))["code__max"]
            self.code = str(int(last_code) + 1) if last_code else "1000"
        super().save(*args, **kwargs)
