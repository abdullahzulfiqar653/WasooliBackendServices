from apis.serializers.presigned_url import PreSignedUrlSerializer
from rest_framework.generics import CreateAPIView
from apis.permissions import IsMerchantOrStaff


class PreSignedUrlCreateAPIView(CreateAPIView):
    """
    This view allows generating a pre-signed URL for uploading files directly to S3.

    The view accepts two body parameters:
    - `s3_key`: The key (path) for the file to be uploaded to S3.
    - `file_type`: The MIME type of the file being uploaded.

    Example request data:
    `{
        "s3_key": "profile/primary/{merchant.id}/{image.jpg}",
        "file_type": "image/jpeg"
    }`
    """

    serializer_class = PreSignedUrlSerializer
    permission_classes = [IsMerchantOrStaff]
