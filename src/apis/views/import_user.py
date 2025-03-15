from apis.permissions import IsMerchantOrStaff
from drf_spectacular.utils import extend_schema
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.response import Response
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
    def post(self, request, *args, **kwargs):
        serializer = BulkCustomerSerializer(data=request.FILES, context={"request": request})  # Use request.FILES
        if serializer.is_valid():
            response_data = serializer.save()
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
