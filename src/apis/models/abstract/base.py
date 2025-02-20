from django.db import models
from django.utils import timezone
from apis.models.mixins.uid import UIDMixin


class BaseModel(models.Model, UIDMixin):
    id = models.CharField(max_length=15, primary_key=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # Ensure the created_at and updated_at fields are timezone-aware
        if self.created_at and timezone.is_naive(self.created_at):
            self.created_at = timezone.make_aware(
                self.created_at, timezone.get_current_timezone()
            )
        if self.updated_at and timezone.is_naive(self.updated_at):
            self.updated_at = timezone.make_aware(
                self.updated_at, timezone.get_current_timezone()
            )
        self.set_uid()
        super().save(**kwargs)
