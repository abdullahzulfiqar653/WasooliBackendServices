from rest_framework import serializers
from apis.models.merchant_membership import MerchantMembership


class MembershipStatusChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MerchantMembership
        fields = ["is_active"]
