from rest_framework import serializers
from apis.models.merchant import Merchant


class MerchantFooterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Merchant
        fields = ["metadata"]

    def update(self, instance, validated_data):
        """
        Update only the 'footer' attribute inside metadata while preserving existing footer fields.
        """

        new_footer_data = validated_data.get("metadata", {}).get("footer", {})

        if new_footer_data:
            validated_data["metadata"]["footer"] = new_footer_data

        return super().update(instance, validated_data)
