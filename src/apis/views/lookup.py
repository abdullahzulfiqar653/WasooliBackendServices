from rest_framework import generics

from apis.models.lookup import Lookup
from apis.serializers.lookup import LookupSerializer


class LookupListAPIView(generics.ListAPIView):
    serializer_class = LookupSerializer
    permission_classes = []
    pagination_class = None

    def get_queryset(self):
        flag = self.kwargs["flag"]
        return Lookup.objects.filter(type__name=flag).prefetch_related("sub_types")
