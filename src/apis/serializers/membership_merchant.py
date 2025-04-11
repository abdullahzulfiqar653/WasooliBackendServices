from rest_framework import serializers
from apis.models.merchant import Merchant


class MembershipMerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = ["id", "name", "is_fixed_fee_merchant"]
