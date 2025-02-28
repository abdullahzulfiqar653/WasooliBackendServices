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

        metadata = instance.metadata if isinstance(instance.metadata, dict) else {}

        footer_data = metadata.get("footer", {})
        new_footer_data = validated_data.get("metadata", {}).get("footer", {})

        if isinstance(footer_data, dict) and isinstance(new_footer_data, dict):
            footer_data.update(new_footer_data)

        metadata["footer"] = footer_data
        instance.metadata = metadata
        instance.save()

        return instance
