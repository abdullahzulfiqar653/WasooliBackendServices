import os

from django.apps import apps
from django.dispatch import receiver
from django.core.management import call_command
from django.db.models.signals import post_migrate


@receiver(post_migrate, sender=apps.get_app_config("apis"))
def load_data_from_fixture(sender, **kwargs):
    lookups_data = os.path.join("apis", "fixtures", "lookups.json")
    call_command("loaddata", lookups_data, app_label="api")
