import django_filters
from apis.models.invoice import Invoice
from django_filters import rest_framework as filters


class InvoiceFilter(filters.FilterSet):
    created_at_year = django_filters.NumberFilter(
        field_name="created_at", lookup_expr="year"
    )
    type = django_filters.CharFilter(field_name="type", lookup_expr="iexact")
    status = django_filters.ChoiceFilter(choices=Invoice.STATUS.choices)

    class Meta:
        model = Invoice
        fields = []
