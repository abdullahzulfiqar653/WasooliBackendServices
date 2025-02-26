from rest_framework import serializers
from apis.models.merchant_membership import MerchantMembership
from apis.models.merchant_member import MerchantMember



class MerchantMembershipStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = MerchantMembership
        fields = ["is_active"]

    def update(self, instance, validated_data):
        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance.save(update_fields=["is_active"])
        return instance

