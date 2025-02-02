from rest_framework import serializers


class DashboardMetricSerializer(serializers.Serializer):
    value = serializers.DecimalField(
        max_digits=10, decimal_places=2, coerce_to_string=False
    )
    name = serializers.CharField()


class MerchantDashboardSerializer(serializers.Serializer):
    total_collections_today = DashboardMetricSerializer()
    total_collections_this_month = DashboardMetricSerializer()
    total_remaining_collections_this_month = DashboardMetricSerializer()
    total_collections = DashboardMetricSerializer()
    total_remaining_collections = DashboardMetricSerializer()
    total_customers = DashboardMetricSerializer()
    active_customers = DashboardMetricSerializer()
    non_active_customers = DashboardMetricSerializer()
