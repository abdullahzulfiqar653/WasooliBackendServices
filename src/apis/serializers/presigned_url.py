from services.s3 import S3Service
from rest_framework import serializers
from botocore.exceptions import NoCredentialsError

s3_client = S3Service()


class PreSignedUrlSerializer(serializers.Serializer):
    file = serializers.ImageField(write_only=True)
    public = serializers.BooleanField(default=True, write_only=True)
    presigned_url = serializers.URLField(read_only=True)

    def create(self, validated_data):
        request = self.context.get("request")
        file = validated_data.get("file")
        file_name = file.name.replace(" ", "_")
        public = validated_data.get("public", True)
        s3_key = f"profile/{request.merchant.id}/{file_name}"

        try:
            presigned_url = s3_client.upload_file(file, s3_key, is_public=public)
            return {"presigned_url": presigned_url}
        except NoCredentialsError:
            raise serializers.ValidationError(
                "AWS credentials are not configured correctly."
            )
        except Exception as e:
            raise serializers.ValidationError(f"Error uploading file: {str(e)}")
