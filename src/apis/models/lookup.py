from django.db import models, Q
from apis.models.abstract.base import BaseModel


class Lookup(BaseModel):
    type = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        related_name="sub_types",
    )
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    @staticmethod
    def get_cities():
        """Retrieve all top-level cities (entries with no parent type)."""
        return Lookup.objects.filter(type__name="City")

    @staticmethod
    def get_areas_by_city(city):
        """Retrieve all areas for a specific city."""
        city = Lookup.objects.filter(
            Q(type__name="City") & (Q(name=city) | Q(id=city))
        ).first()
        return Lookup.objects.filter(type=city) if city else Lookup.objects.none()
