from rest_framework.generics import UpdateAPIView
from apis.models.merchant_member import MerchantMember
from apis.serializers.push_notifications import (
    MerchantMemberPushNotifcationIDSerializer,
)


class UpdatePushNotificationID(UpdateAPIView):
    serializer_class = MerchantMemberPushNotifcationIDSerializer

    def get_object(self):
        merchant_member = MerchantMember.objects.get(user=self.request.user)
        return merchant_member

