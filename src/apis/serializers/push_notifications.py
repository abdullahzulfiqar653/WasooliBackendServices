from rest_framework import serializers
from apis.models.merchant_member import MerchantMember

class MerchantMemberPushNotifcationIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = MerchantMember
        fields = ["push_notification_id"]

    def update(self, instance, validated_data):
        instance.push_notification_id=validated_data.get("push_notification_id",instance.push_notification_id)
        instance.save(update_fields=["push_notification_id"])
        return instance 
    