from django.db import models
from django.contrib.auth.models import User
from apis.models.abstract.base import BaseModel


class Merchant(BaseModel):
    class MerchantType(models.TextChoices):
        INTERNET = "internet", "Internet"
        WATER = "water", "Water"
        MILK = "milk", "Milk"
        TV = "tv", "TV"
        GYM = "gym", "Gym"
        GARBAGE = "garbage", "Garbage"

    name = models.CharField(max_length=50)
    type = models.CharField(max_length=50, choices=MerchantType.choices)
    owner = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="merchant"
    )

    def __str__(self):
        return f"{self.name} ({self.code})"
