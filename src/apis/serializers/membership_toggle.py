from rest_framework import serializers
from apis.models.merchant_membership import MerchantMembership


class MembershipToggleSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField()

    class Meta:
        model = MerchantMembership
        fields = ["is_active"]

    def update(self, instance, validated_data):
        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance.save()
        return instance
