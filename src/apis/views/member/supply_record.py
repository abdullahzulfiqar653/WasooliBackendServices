from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend

from apis.permissions import IsMerchantOrStaff
from apis.models.supply_record import SupplyRecord
from apis.filters.supply_record import SupplyRecordFilter
from apis.serializers.supply_record import SupplyRecordSerializer

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


class MemberSupplyRecordListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = SupplyRecordSerializer
    permission_classes = [IsMerchantOrStaff]
    filter_backends = (DjangoFilterBackend,)
    pagination_class = None
    filterset_class = SupplyRecordFilter
    queryset = SupplyRecord.objects.none()

    def get_queryset(self):
        return self.request.membership.supply_records.all()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="created_at_year",
                description="Year of creation for filtering supply records",
                required=True,
                type=OpenApiTypes.INT,
            ),
            OpenApiParameter(
                name="created_at_month",
                description="Month of creation for filtering supply records",
                required=True,
                type=OpenApiTypes.INT,
            ),
        ],
        description="""
\nRetrieves a list of supply records associated with the user's membership, filtered by the specified year and month of creation.
\nThis view supports the following filters:
    \n- `created_at_year` : Specifies the year when the supply records were created. This filter is required.
    \n- `created_at_month` : Specifies the month when the supply records were created. This filter is required.
\nThe response will include all matching supply records based on the filtering criteria provided in the request.
        """,
        responses={
            200: SupplyRecordSerializer(many=True),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        request=SupplyRecordSerializer,
        description="""
        \nCreates a new supply record for the customer or updates the existing one for the given day.
        \n- **Only one record per day can be created**. If a record already exists for the day, it will be updated with the new values.
        \nFor example:
            \n- Merchant added 1 "given" and 2 "taken", then added 2 "given" and 1 "taken". 
            \n- The record will be updated to reflect 2 "given" and 1 "taken" for that day.
        \n**Note:** Only authenticated merchants or staff can create or update supply records.
        """,
        responses={
            201: SupplyRecordSerializer,
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
