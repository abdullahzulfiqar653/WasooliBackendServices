from rest_framework import serializers


class MemberProfileMetricSerializer(serializers.Serializer):
    value = serializers.DecimalField(
        max_digits=10, decimal_places=2, coerce_to_string=False
    )
    name = serializers.CharField()


class MemberProfileSerializer(serializers.Serializer):
    total_spend = MemberProfileMetricSerializer()
    total_remaining = MemberProfileMetricSerializer()
    total_saved = MemberProfileMetricSerializer()
