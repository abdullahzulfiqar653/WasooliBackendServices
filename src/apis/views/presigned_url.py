from apis.serializers.presigned_url import PreSignedUrlSerializer
from rest_framework.generics import CreateAPIView
from apis.permissions import IsMerchantOrStaff

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


@extend_schema(
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "file": {"type": "string", "format": "binary"},  # Fix for file upload
                "public": {"type": "boolean"},
            },
            "required": ["file"],
        }
    },
    responses={200: PreSignedUrlSerializer},
)
class PreSignedUrlCreateAPIView(CreateAPIView):
    """
    This endpoint generates a **pre-signed URL** for securely uploading files directly to **Amazon S3**.

    **Request:**
    - Accepts the following **body parameters**:

      | Parameter | Required | Description |
      |-----------|--------  | -------------|
      | file    | ✅ Yes   | The file that will be uploaded. |
      | public  | ❌ No    | If true, the file will be publicly accessible. Default is true. |

    **Headers:**
    - Authorization: Token your_auth_token *(Required)*

    **Response:**
    - Returns a **pre-signed URL** that the client can use to upload the file directly to S3.
    """

    serializer_class = PreSignedUrlSerializer
    permission_classes = [IsMerchantOrStaff]
