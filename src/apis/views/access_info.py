from rest_framework import generics
from rest_framework.response import Response

from apis.permissions import IsMerchantOrStaff
from django.contrib.auth.models import Permission
from apis.serializers.access_info import AccessInfoSerializer
from apis.models.member_role import RoleChoices


class AccessInfoRetrieveAPIView(generics.RetrieveAPIView):
    """
    This endpoint provides all necessary information for accessing other endpoints.

    **Response Includes:**
    - The user's **merchant ID** and **member ID**.

    - A detailed list of **permissions** assigned to the user.

    - Whether the merchant has a **fixed fee structure**.
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

        # Using prefetch_related for optimizing the roles query
        is_merchant = (
            request.user.profile.roles.filter(role=RoleChoices.MERCHANT)
            .prefetch_related("roles")
            .exists()
        )

        return Response(
            {
                "is_merchant": is_merchant,
                "permissions": grouped_permissions,
                "merchant_id": request.merchant.id,
                "member_id": request.user.profile.id,
                "merchant_name": request.merchant.name,
                "merchant_type": request.merchant.type,
                "is_fixed_fee_merchant": request.merchant.is_fixed_fee_merchant,
            }
        )
