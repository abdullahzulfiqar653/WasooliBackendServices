from services.s3 import S3Service
from rest_framework import serializers
from botocore.exceptions import NoCredentialsError

from apis.common.contants import ALLOWED_FILE_TYPES, ALLOWED_IMAGE_EXTENSIONS

s3_client = S3Service()


class PreSignedUrlSerializer(serializers.Serializer):
    s3_key = serializers.CharField(max_length=1000, write_only=True)
    file_type = serializers.CharField(max_length=50, write_only=True)
    presigned_url = serializers.URLField(read_only=True)

    def validate_s3_key(self, value):
        """Validate the s3_key for correct file extensions."""
        if not value.endswith(ALLOWED_IMAGE_EXTENSIONS):
            raise serializers.ValidationError(
                f"Invalid file type for s3_key. Allowed formats: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}."
            )
        return value

    def validate_file_type(self, value):
        """Validate the file_type for allowed mime types."""
        if value not in ALLOWED_FILE_TYPES:
            raise serializers.ValidationError(
                f"Invalid file type. Allowed types: {', '.join(ALLOWED_FILE_TYPES)}"
            )
        return value

    def create(self, validated_data):
        s3_key = validated_data["s3_key"]
        file_type = validated_data["file_type"]
        try:
            presigned_url = s3_client.generate_presigned_url_for_upload(
                s3_key, file_type
            )
            return {"presigned_url": presigned_url}

        except NoCredentialsError:
            raise serializers.ValidationError(
                "AWS credentials are not configured correctly."
            )
