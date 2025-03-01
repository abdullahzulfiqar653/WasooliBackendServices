from django.db import models

from apis.models.abstract.base import BaseModel


class MerchantMember(BaseModel):
    UID_PREFIX = 105
    user = models.OneToOneField(
        "auth.User", on_delete=models.CASCADE, related_name="profile"
    )
    merchant = models.ForeignKey(
        "apis.Merchant",
        on_delete=models.SET_NULL,
        null=True,
        related_name="staff_members",
    )

    cnic = models.CharField(max_length=13, null=True, blank=True)
    picture = models.CharField(max_length=256, blank=True, null=True)
    push_notification_id = models.CharField(max_length=56, blank=True, null=True)
    primary_phone = models.CharField(
        max_length=10, verbose_name="Primary Phone", unique=True
    )
    code = models.CharField(max_length=6, unique=True, editable=False)
    merchant_memberships = models.ManyToManyField(
        "apis.Merchant",
        through="MerchantMembership",
        related_name="customer_memberships",
    )

    class Meta:
        verbose_name = "Members Register"
        unique_together = [["user", "cnic", "primary_phone"]]
        indexes = [
            models.Index(fields=["cnic"]),
            models.Index(fields=["code"]),
            models.Index(fields=["user"]),
            models.Index(fields=["merchant"]),
            models.Index(fields=["-created_at"]),
            models.Index(fields=["primary_phone"]),
        ]
        permissions = [
            # Staff permissions
            ("add_staff", "Can add staff"),
            ("view_staff", "Can view staff"),
            ("change_staff", "Can change staff"),
            # Customer permissions
            ("add_customers", "Can add customers"),
            ("view_customers", "Can view customers"),
            ("change_customers", "Can change customers"),
            # Excel Download permissions
            ("view_pdf", "Can download PDF"),
            ("view_excel", "Can download Excel"),
            # Dashboard
            ("view_dashboard", "Can view dashboard"),
        ]

    def __str__(self):
        return f"{self.code}"

    def save(self, *args, **kwargs):
        if not self.code:
            last_code = MerchantMember.objects.aggregate(models.Max("code"))[
                "code__max"
            ]
            self.code = str(int(last_code) + 1) if last_code else "1000"
        super().save(*args, **kwargs)
