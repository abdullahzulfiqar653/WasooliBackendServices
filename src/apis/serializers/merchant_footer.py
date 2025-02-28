from rest_framework import serializers
from apis.models.merchant import Merchant


class MerchantMetadataSerializer(serializers.Serializer):
    key = serializers.CharField()
    value = serializers.CharField()


class MerchantFooterSerializer(serializers.ModelSerializer):
    metadata = MerchantMetadataSerializer(many=True)

    class Meta:
        model = Merchant
        fields = ["metadata"]

    def update(self, instance, validated_data):
        instance.metadata = validated_data.get("metadata", instance.metadata)
        instance.save()
        return instance
