from rest_framework import generics

from apis.models.lookup import Lookup
from apis.serializers.lookup import LookupSerializer


class LookupListAPIView(generics.ListAPIView):
    """
    This endpoint is used to retrieve lookup information.

    - You need to pass a single parameter, `value`.
    - Current supported flags are:
    - `city`: Returns a list of cities along with their associated child areas.
    - `keys`: Returns a list of metadata keys so if user adding extra fields then he get suggestions.

    Based on the provided flag, the response will include the relevant data and its child objects.
    """

    serializer_class = LookupSerializer
    permission_classes = []
    pagination_class = None

    def get_queryset(self):
        flag = self.kwargs["flag"]
        return Lookup.objects.filter(type__name=flag).prefetch_related("sub_types")
