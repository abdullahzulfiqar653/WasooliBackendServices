from rest_framework import serializers
from apis.models.merchant_member import MerchantMember

class MerchantMemberpsuhSerializer(serializers.ModelSerializer):
    class Meta:
        model = MerchantMember
        fields = ["push_notification_id"]