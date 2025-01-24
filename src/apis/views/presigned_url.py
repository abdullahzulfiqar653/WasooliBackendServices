from apis.serializers.presigned_url import PreSignedUrlSerializer
from rest_framework.generics import CreateAPIView
from apis.permissions import IsMerchantOrStaff


class PreSignedUrlCreateAPIView(CreateAPIView):
    """
    This view allows generating a pre-signed URL for uploading files directly to S3.

    The view accepts two body parameters:
    - `file`: file user want to upload.
    - `public`: file visibility. If set to `true`, the file will be publicly accessible. Default is `true`.
    """

    serializer_class = PreSignedUrlSerializer
    permission_classes = [IsMerchantOrStaff]
