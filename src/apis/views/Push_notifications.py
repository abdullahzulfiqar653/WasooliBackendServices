from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apis.models.merchant_member import MerchantMember
from apis.serializers import MerchantMemberpsuhSerializer

class UpdatePushNotificationID(APIView):
    serializer_class=MerchantMemberpsuhSerializer
    def post(self, request):
        user = request.user
        push_notification_id = request.data.get("push_notification_id")

        if not push_notification_id:
            return Response(
                {"error": "Push notification ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            merchant_member = MerchantMember.objects.get(user=user)
            merchant_member.push_notification_id = push_notification_id
            merchant_member.save()

            return Response(
                {"message": "Push notification ID updated successfully"},
                status=status.HTTP_200_OK
            )

        except MerchantMember.DoesNotExist:
            return Response(
                {"error": "MerchantMember not found"},
                status=status.HTTP_404_NOT_FOUND
            )
