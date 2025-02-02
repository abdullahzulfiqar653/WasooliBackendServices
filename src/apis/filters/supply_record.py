import django_filters
from django_filters import rest_framework as filters
from apis.models.supply_record import SupplyRecord


class SupplyRecordFilter(filters.FilterSet):
    created_at_year = django_filters.NumberFilter(
        field_name="created_at", lookup_expr="year"
    )
    created_at_month = django_filters.NumberFilter(
        field_name="created_at", lookup_expr="month"
    )

    class Meta:
        model = SupplyRecord
        fields = []
