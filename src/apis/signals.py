import os

from django.apps import apps
from django.dispatch import receiver
from django.core.management import call_command
from django.db.models.signals import post_migrate, post_save

from apis.models.merchant import Merchant
from django.contrib.auth.models import Group
from apis.models.merchant_member import MerchantMember
from apis.models.member_role import RoleChoices, MemberRole


@receiver(post_migrate, sender=apps.get_app_config("apis"))
def load_data_from_fixture(sender, **kwargs):
    lookups_data = os.path.join("apis", "fixtures", "lookups.json")
    call_command("loaddata", lookups_data, app_label="api")


@receiver(post_save, sender=Merchant)
def create_merchant_member(sender, instance, created, **kwargs):
    if created:
        instance.owner.groups.add(Group.objects.get(name=RoleChoices.MERCHANT))
        member = MerchantMember.objects.create(user=instance.owner, merchant=instance)
        MemberRole.objects.create(member=member, role=RoleChoices.MERCHANT)
