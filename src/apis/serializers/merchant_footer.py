from rest_framework import serializers
from apis.models.merchant import Merchant


class MerchantFooterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = ["metadata"]

    def validate_metadata(self, value):
        """Ensure metadata is a dictionary."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Metadata must be a dictionary.")
        return value

    def update(self, instance, validated_data):
        """
        Update only the 'footer' attribute inside metadata while preserving existing footer fields.
        """
        metadata = instance.metadata or {}
        # Update footer fields while preserving existing data
        metadata["footer"] = validated_data["metadata"]
        
        # Ensure validated_data contains the updated metadata
        validated_data["metadata"] = metadata

        return super().update(instance, validated_data)
