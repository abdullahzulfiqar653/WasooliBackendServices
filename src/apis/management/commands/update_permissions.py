from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from apis.common.contants import MERCHANT_PERMISSIONS, STAFF_PERMISSIONS


class Command(BaseCommand):
    help = "Assign or update permissions for Staff and Merchant groups"

    def handle(self, *args, **kwargs):
        staff_group, _ = Group.objects.get_or_create(name="Staff")
        merchant_group, _ = Group.objects.get_or_create(name="Merchant")
        customer_group, _ = Group.objects.get_or_create(name="Customer")

        staff_group.permissions.clear()
        merchant_group.permissions.clear()

        # Assign permissions based on the rules to Merchant
        for model_name, allowed_perms in MERCHANT_PERMISSIONS.items():
            permissions = Permission.objects.filter(content_type__model=model_name)

            # Filter permissions based on the allowed list
            filtered_permissions = permissions.filter(codename__in=allowed_perms)
            merchant_group.permissions.add(*filtered_permissions)

        # Assign permissions based on the rules to Staff
        for model_name, allowed_perms in STAFF_PERMISSIONS.items():
            permissions = Permission.objects.filter(content_type__model=model_name)

            # Filter permissions based on the allowed list
            filtered_permissions = permissions.filter(codename__in=allowed_perms)
            staff_group.permissions.add(*filtered_permissions)

        # Display the results
        self.stdout.write(self.style.SUCCESS("Permissions successfully assigned!"))
