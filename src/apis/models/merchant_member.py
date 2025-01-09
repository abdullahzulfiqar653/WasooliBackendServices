from django.db import models

from apis.models.abstract.base import BaseModel


class MerchantMember(BaseModel):
    # TODO if a merchant registered with someone as a customer need to handle that situation
    user = models.OneToOneField(
        "auth.User", on_delete=models.CASCADE, related_name="profile"
    )
    memberships = models.ManyToManyField(
        "apis.Merchant", through="MerchantMembership", related_name="users"
    )
    cnic = models.CharField(max_length=13, null=True)
    picture = models.ImageField(upload_to="protected/picture", null=True)
    primary_phone = models.CharField(
        max_length=10, null=True, verbose_name="Primary Phone", unique=True
    )
    code = models.CharField(max_length=6, unique=True, editable=False)

    class Meta:
        verbose_name = "MerchantsMembersRegister"
        unique_together = [["user", "cnic", "primary_phone"]]

    def __str__(self):
        return f"{self.user.first_name}"

    def save(self, *args, **kwargs):
        if not self.code:
            last_code = MerchantMember.objects.aggregate(models.Max("code"))[
                "code__max"
            ]
            self.code = str(int(last_code) + 1) if last_code else "1000"
        super().save(*args, **kwargs)
