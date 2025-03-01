from apis.permissions import IsMerchantOrStaff
from drf_spectacular.utils import extend_schema
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import MultiPartParser, FormParser


from apis.serializers.bulk_customer_serialzier import BulkCustomerSerializer


@extend_schema(
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "file": {"type": "string", "format": "binary"},
            },
            "required": ["file"],
        }
    },
)
class MerchantMemberCSVUploadView(CreateAPIView):
    permission_classes = [IsMerchantOrStaff]
    serializer_class = BulkCustomerSerializer
    parser_classes = (MultiPartParser, FormParser)
