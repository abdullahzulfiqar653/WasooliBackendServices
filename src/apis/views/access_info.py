from rest_framework import generics
from rest_framework.response import Response
from apis.permissions import IsMerchantOrStaff
from django.contrib.auth.models import Permission
from apis.serializers.access_info import AccessInfoSerializer


class AccessInfoRetrieveAPIView(generics.RetrieveAPIView):
    """
    This endpoint provides all the necessary information for accessing other endpoints, including:
    - The user's merchant ID and member ID.
    - The permissions assigned to them.
    """

    permission_classes = [IsMerchantOrStaff]
    serializer_class = AccessInfoSerializer

    def retrieve(self, request, *args, **kwargs):
        direct_permissions = request.user.user_permissions.all()
        group_permissions = Permission.objects.filter(group__user=request.user)
        all_permissions = direct_permissions | group_permissions
        grouped_permissions = {}

        for perm in all_permissions.distinct():
            model_name = perm.content_type.model
            grouped_permissions.setdefault(model_name, []).append(perm.codename)

        for model, actions in grouped_permissions.items():
            grouped_permissions[model] = sorted(set(actions))

        return Response(
            {
                "permissions": grouped_permissions,
                "merchant_id": request.merchant.id,
                "member_id": request.user.profile.id,
            }
        )
