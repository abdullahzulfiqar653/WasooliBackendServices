from rest_framework.generics import UpdateAPIView
from apis.serializers import MerchantMembershipStatusSerializer
from apis.permissions import IsMerchantOrStaff

class MembershipstatusAPIView(UpdateAPIView):
    serializer_class = MerchantMembershipStatusSerializer
    permission_classes = [IsMerchantOrStaff]


    def get_object(self):
        return self.request.membership